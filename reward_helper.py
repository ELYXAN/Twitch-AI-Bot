import json
import logging
import sys
from pathlib import Path
from typing import List, Dict

import requests

from main import get_new_twitch_token

CONFIG_PATH = Path(__file__).with_name("config.json")

if not CONFIG_PATH.exists():
    raise SystemExit("config.json fehlt – bitte zuerst aus main.py übernehmen.")

with CONFIG_PATH.open("r", encoding="utf-8") as cfg_file:
    config = json.load(cfg_file)

try:
    twitch_cfg = config["twitch"]
except KeyError as exc:
    raise SystemExit("config.json benötigt den Block 'twitch'.") from exc

TWITCH_CLIENT_ID = twitch_cfg["client_id"]
TWITCH_CLIENT_SECRET = twitch_cfg["client_secret"]
TWITCH_REFRESH_TOKEN = twitch_cfg["refresh_token"]
TWITCH_CHANNEL = twitch_cfg["channel"]

logging.basicConfig(level=logging.INFO)


def get_broadcaster_id(channel_name: str, access_token: str) -> str:
    """Return the broadcaster ID for the given channel login."""
    url = "https://api.twitch.tv/helix/users"
    headers = {
        "Client-ID": TWITCH_CLIENT_ID,
        "Authorization": f"Bearer {access_token}",
    }
    params = {"login": channel_name}

    resp = requests.get(url, headers=headers, params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json().get("data", [])

    if not data:
        raise RuntimeError(f"No Twitch user found for channel '{channel_name}'.")

    return data[0]["id"]


def get_custom_rewards(broadcaster_id: str, access_token: str) -> List[Dict]:
    """Fetch all custom channel point rewards for the broadcaster."""
    url = "https://api.twitch.tv/helix/channel_points/custom_rewards"
    headers = {
        "Client-ID": TWITCH_CLIENT_ID,
        "Authorization": f"Bearer {access_token}",
    }
    params = {
        "broadcaster_id": broadcaster_id,
    }

    resp = requests.get(url, headers=headers, params=params, timeout=15)
    print(resp.text)
    resp.raise_for_status()
    return resp.json().get("data", [])


def main() -> None:
    logging.info("Requesting fresh access token via refresh token...")
    access_token = get_new_twitch_token()
    if not access_token:
        logging.error("Unable to fetch access token. Check refresh token and credentials.")
        sys.exit(1)

    channel = TWITCH_CHANNEL.strip()
    if not channel:
        logging.error("TWITCH_CHANNEL is empty in main.py. Please set it and rerun.")
        sys.exit(1)

    try:
        broadcaster_id = get_broadcaster_id(channel, access_token)
        logging.info("Resolved channel '%s' to broadcaster_id %s", channel, broadcaster_id)

        rewards = get_custom_rewards(broadcaster_id, access_token)
        print(rewards)
        if not rewards:
            logging.warning("No custom rewards returned. Check if the bot account has manage permission and the reward exists.")
            return

        print("\nCustom rewards for", channel)
        print("=" * 40)
        for reward in rewards:
            print(f"Name: {reward['title']}")
            print(f"ID:   {reward['id']}")
            print(f"Cost: {reward['cost']} channel points")
            print("-" * 40)

    except requests.HTTPError as http_err:
        logging.error("HTTP error: %s", http_err)
        if http_err.response is not None:
            logging.error("Response: %s", http_err.response.text)
        sys.exit(1)
    except Exception as exc:
        logging.error("Unexpected error: %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
