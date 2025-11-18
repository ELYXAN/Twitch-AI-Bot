import asyncio
import json
import logging
import ssl
from pathlib import Path

import requests
from openai import OpenAI

# --- CONFIGURATION ---
CONFIG_PATH = Path(__file__).with_name("config.json")
IRC_SERVER = "irc.chat.twitch.tv"
IRC_PORT = 6697


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        raise SystemExit(
            "config.json nicht gefunden. Kopiere config.json (oder erstelle sie) und trage deine Secrets dort ein."
        )

    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        raw_config = json.load(f)

    try:
        twitch_cfg = raw_config["twitch"]
        openai_cfg = raw_config["openai"]
    except KeyError as exc:
        raise SystemExit("config.json muss die Bereiche 'twitch' und 'openai' enthalten.") from exc

    required_twitch = [
        "client_id",
        "client_secret",
        "refresh_token",
        "bot_nick",
        "channel",
        "custom_reward_id",
    ]
    missing_twitch = [key for key in required_twitch if not twitch_cfg.get(key)]
    if missing_twitch:
        raise SystemExit(f"In config.json fehlen Twitch-Werte: {', '.join(missing_twitch)}")

    if not openai_cfg.get("api_key"):
        raise SystemExit("In config.json fehlt openai.api_key.")

    return raw_config


CONFIG = load_config()
TWITCH_CLIENT_ID = CONFIG["twitch"]["client_id"]
TWITCH_CLIENT_SECRET = CONFIG["twitch"]["client_secret"]
TWITCH_REFRESH_TOKEN = CONFIG["twitch"]["refresh_token"]
TWITCH_BOT_NICK = CONFIG["twitch"]["bot_nick"]
TWITCH_CHANNEL = CONFIG["twitch"]["channel"]
CUSTOM_REWARD_ID = CONFIG["twitch"]["custom_reward_id"]

OPENAI_API_KEY = CONFIG["openai"]["api_key"]

# --- INITIALIZATION ---
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
client = OpenAI(api_key=OPENAI_API_KEY)


def get_new_twitch_token():
    """Fetches a new access token from the Twitch API using the refresh token."""
    url = "https://id.twitch.tv/oauth2/token"
    params = {
        'client_id': TWITCH_CLIENT_ID,
        'client_secret': TWITCH_CLIENT_SECRET,
        'grant_type': 'refresh_token',
        'refresh_token': TWITCH_REFRESH_TOKEN
    }
    try:
        response = requests.post(url, data=params)
        response.raise_for_status()
        return response.json()['access_token']
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching new token: {e}")
        return None


def validate_access_token(access_token: str) -> dict | None:
    """Validate the access token and ensure required scopes are present."""
    url = "https://id.twitch.tv/oauth2/validate"
    headers = {
        "Authorization": f"OAuth {access_token}",
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        required_scopes = {"chat:read", "chat:edit", "channel:read:redemptions"}
        token_scopes = set(data.get("scopes", []))
        missing = required_scopes - token_scopes
        if missing:
            logging.error("Access token is missing required scopes: %s", ", ".join(sorted(missing)))
            return None

        if data.get("login") != TWITCH_BOT_NICK.lower():
            logging.error(
                "Access token belongs to '%s', but TWITCH_BOT_NICK is '%s'.",
                data.get("login"),
                TWITCH_BOT_NICK,
            )
            return None

        logging.info(
            "Token valid for user '%s' with scopes: %s",
            data.get("login"),
            ", ".join(sorted(token_scopes)),
        )
        return data

    except requests.exceptions.RequestException as e:
        logging.error("Token validation failed: %s", e)
        if hasattr(e, "response") and e.response is not None:
            logging.error("Response: %s", e.response.text)
        return None


class IRCBot:

    def __init__(self, access_token: str):
        self.access_token = access_token
        self.reader: asyncio.StreamReader | None = None
        self.writer: asyncio.StreamWriter | None = None

    async def connect(self):
        context = ssl.create_default_context()
        self.reader, self.writer = await asyncio.open_connection(
            IRC_SERVER, IRC_PORT, ssl=context
        )
        logging.info("Verbunden mit IRC %s:%s", IRC_SERVER, IRC_PORT)
        await self.send_raw("CAP REQ :twitch.tv/tags twitch.tv/commands twitch.tv/membership")
        await self.send_raw(f"PASS oauth:{self.access_token}")
        await self.send_raw(f"NICK {TWITCH_BOT_NICK}")
        await self.send_raw(f"JOIN #{TWITCH_CHANNEL}")

        print("-" * 30)
        print(f"✅ AIBot '{TWITCH_BOT_NICK}' ist via IRC verbunden.")
        print(f"✅ Lauscht in channel: #{TWITCH_CHANNEL}")
        print(f"✅ Beobachtet Reward ID: {CUSTOM_REWARD_ID}")
        print("-" * 30)

    async def send_raw(self, payload: str):
        assert self.writer is not None
        message = f"{payload}\r\n"
        logging.debug("[IRC>>] %s", payload)
        self.writer.write(message.encode("utf-8"))
        await self.writer.drain()

    async def send_chat(self, text: str):
        await self.send_raw(f"PRIVMSG #{TWITCH_CHANNEL} :{text}")

    async def listen(self):
        assert self.reader is not None
        while True:
            line = await self.reader.readline()
            if not line:
                logging.warning("Verbindung zur IRC-Server wurde geschlossen.")
                break
            decoded = line.decode("utf-8", errors="ignore").strip()
            logging.debug("[IRC<<] %s", decoded)

            if decoded.startswith("PING"):
                await self.send_raw(decoded.replace("PING", "PONG", 1))
                continue

            tags, prefix, command, params, trailing = parse_irc_message(decoded)

            if command == "PRIVMSG":
                user = prefix.split("!")[0] if prefix else "unknown"
                logging.debug("[CHAT] author=%s content=%s tags=%s", user, trailing, tags)
                if tags.get("custom-reward-id") == CUSTOM_REWARD_ID:
                    await handle_reward(prompt=trailing, user=user, bot=self)

            elif command == "USERNOTICE" and tags.get("msg-id") == "reward-redeem":
                if tags.get("custom-reward-id") != CUSTOM_REWARD_ID:
                    continue
                user_input = tags.get("msg-param-user-input", "").strip()
                user = tags.get("display-name") or tags.get("login") or "unknown"
                if not user_input:
                    logging.warning("Reward redeemed ohne Text; wird ignoriert.")
                    continue
                await handle_reward(prompt=user_input, user=user, bot=self)

    async def run(self):
        await self.connect()
        await self.listen()


# --- IRC HELPERS ---
def parse_irc_message(raw: str):
    tags = {}
    prefix = ""
    trailing = ""

    if raw.startswith("@"):
        tags_part, raw = raw.split(" ", 1)
        for part in tags_part[1:].split(";"):
            if "=" in part:
                k, v = part.split("=", 1)
            else:
                k, v = part, ""
            if v:
                v = v.replace("\\s", " ").replace("\\:", ";")
            tags[k] = v

    if raw.startswith(":"):
        prefix, raw = raw[1:].split(" ", 1)

    if " :" in raw:
        raw, trailing = raw.split(" :", 1)

    parts = raw.split()
    command = parts[0] if parts else ""
    params = parts[1:]
    return tags, prefix, command, params, trailing


async def handle_reward(prompt: str, user: str, bot: IRCBot):
    logging.info("-> Reward redeemed by '%s': '%s'", user, prompt)

    try:
        #await bot.send_chat(f"@{user} deine Anfrage wird verarbeitet...")

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful Twitch chatbot. Keep your answers brief and concise, under 400 characters."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100,
            temperature=0.7
        )

        ai_response = response.choices[0].message.content.strip()

        logging.info("<- Sending AI response to '%s': '%s'", user, ai_response)
        await bot.send_chat(f"🤖 @{user}: {ai_response}")

    except Exception as e:
        logging.error("!!! OpenAI request failed: %s", e)
        await bot.send_chat(f"@{user}, es gab einen Fehler bei der AI-Anfrage. 😵")


# --- STARTUP LOGIC ---
if __name__ == "__main__":
    print("Starting AI Bot...")
    access_token = get_new_twitch_token()

    if not access_token:
        print("!!! FATAL: Could not start bot. Failed to get a valid token.")
        raise SystemExit(1)

    validation = validate_access_token(access_token)
    if not validation:
        print("!!! FATAL: Token validation failed. Please re-run the OAuth flow with the proper account and scopes.")
        raise SystemExit(1)

    bot = IRCBot(access_token=access_token)
    try:
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        print("Bot wurde manuell beendet.")
