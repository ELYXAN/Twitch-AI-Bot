import requests
import logging
from twitchio.ext import commands
from openai import OpenAI

# --- CONFIGURATION ---
TWITCH_CLIENT_ID = "YOUR_CLIENT_ID"
TWITCH_CLIENT_SECRET = "YOUR_CLIENT_SECRET"
TWITCH_REFRESH_TOKEN = "YOUR_REFRESH_TOKEN"

TWITCH_BOT_NICK = "your_bot_username"      # e.g., my_cool_bot
TWITCH_CHANNEL = "your_channel_name"       # Your main streaming channel
CUSTOM_REWARD_ID = "YOUR_REWARD_ID_HERE"

OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"

# --- INITIALIZATION ---
logging.basicConfig(level=logging.INFO)
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

# --- BOT CLASS ---
class AIBot(commands.Bot):

    def __init__(self, token):
        super().__init__(
            token=token,
            nick=TWITCH_BOT_NICK,
            prefix="!",  # Not actively used but required
            initial_channels=[TWITCH_CHANNEL]
        )

    async def event_ready(self):
        """Called when the bot has successfully connected and joined the channel."""
        channel_name = self.connected_channels[0].name
        print("-" * 30)
        print(f"✅ AIBot '{self.nick}' is connected.")
        print(f"✅ Listening in channel: #{channel_name}")
        print(f"✅ Responding to Reward ID: {CUSTOM_REWARD_ID}")
        print("-" * 30)
        await self.get_channel(channel_name).send("🤖 AI Bot is now online.")

    async def event_message(self, message):
        """Processes incoming chat messages."""
        if message.echo:
            return

        if message.tags and message.tags.get("custom-reward-id") == CUSTOM_REWARD_ID:
            prompt = message.content
            user = message.author.name
            
            logging.info(f"-> Reward redeemed by '{user}': '{prompt}'")
            
            try:
                await message.channel.send(f"🤖 @{user}, your request is being processed...")

                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are a helpful Twitch chatbot. Keep your answers brief and concise, under 400 characters."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=80,
                    temperature=0.7
                )
                
                ai_response = response.choices[0].message.content.strip()

                logging.info(f"<- Sending AI response to '{user}': '{ai_response}'")
                await message.channel.send(f"🤖 @{user}: {ai_response}")

            except Exception as e:
                logging.error(f"!!! OpenAI request failed: {e}")
                await message.channel.send(f"@{user}, there was an error with the AI request. 😵")

# --- STARTUP LOGIC ---
if __name__ == "__main__":
    print("Starting AI Bot...")
    access_token = get_new_twitch_token()

    if access_token:
        bot_token = f"oauth:{access_token}"
        bot = AIBot(token=bot_token)
        bot.run()
    else:
        print("!!! FATAL: Could not start bot. Failed to get a valid token.")
