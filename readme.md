# 🤖 Twitch AI Chatbot via Channel Points

A Python bot that connects to your Twitch chat, listens for a specific channel point reward, and uses the OpenAI API (e.g., `gpt-4o`) to answer user prompts directly in chat.


![Demo GIF — replace this URL with your own GIF](https://placehold.co/600x200?text=Replace+with+your+GIF)

---

## ✨ Features

- **Channel Point Integration:** Triggers only on a custom channel point reward that you specify.
- **OpenAI API Integration:** Leverages modern language models like `gpt-4o` or `gpt-3.5-turbo` to generate intelligent responses.
- **Automatic Token Refresh:** Uses a secure refresh token mechanism to automatically and safely authenticate with Twitch on every startup. No more manual password updates.
- **Customizable Personality:** The system prompt can be easily modified to give the bot a unique personality.
- **Simple Configuration:** All important settings are collected at the top of the script for easy access.

---

## 🛠️ Setup & Installation

Follow these steps to get the bot running for your channel.

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/Twitch-AI-Bot.git
cd Twitch-AI-Bot
```

### 2. Create a Virtual Environment

It is highly recommended to use a virtual environment to keep dependencies clean.

```bash
# Create the environment
python3 -m venv venv

# Activate the environment
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install twitchio openai requests
```

---

## ⚙️ Configuration

Open `main.py` and fill in the following configuration variables with your own data.

### Twitch Configuration

- `TWITCH_CLIENT_ID` & `TWITCH_CLIENT_SECRET`  
  1. Go to the Twitch Developer Console.  
  2. Register a new application (Category: **Chat Bot**).  
  3. Set the **OAuth Redirect URL** to `http://localhost:3000`.  
  4. Copy the Client ID and generate/copy the Client Secret.

- `TWITCH_REFRESH_TOKEN`  
  You must generate this token one time. Follow the Twitch **Authorization Code Grant Flow** (official Twitch guide). This process gives you the long-lived refresh token required for the script. **Important:** Generate this token for the bot account.

- `TWITCH_BOT_NICK`  
  The username of your bot account (all lowercase). Creating a separate Twitch account for your bot is highly recommended.

- `TWITCH_CHANNEL`  
  The name of your main streaming channel where the bot will operate (all lowercase).

### OpenAI Configuration

- `OPENAI_API_KEY` — Find your API key in your OpenAI Dashboard and paste it into the config.

### Channel Reward Configuration

- `CUSTOM_REWARD_ID`  
  1. In your Twitch Creator Dashboard, create a new Channel Point Reward. **Important:** Enable **Requires Viewer to Enter Text**.  
  2. Run the included `get_rewards.py` script to list the IDs of all your rewards.  
  3. Copy the correct ID and paste it into your config.

---

## ▶️ Running the Bot

Make sure your virtual environment (`venv`) is activated and all configuration variables are set. Then start the script:

```bash
python main.py
```

If everything is correct, you will see a success message in your terminal, and the bot will post an "online" message in your Twitch chat.

---

## 🎨 Customization

You can easily customize the bot's behavior.

### Changing the AI's Personality

Modify the system prompt in the `event_message` function to control the AI's personality and behavior:

```python
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        # CHANGE THIS LINE:
        {"role": "system", "content": "You are a grumpy robot who answers questions reluctantly."},
        {"role": "user", "content": prompt}
    ],
    # ...
)
```

### Changing the AI Model

Change the `model` argument to use a different OpenAI model (e.g., for performance or cost). `gpt-4o` is an excellent modern choice.

```python
response = client.chat.completions.create(
    model="gpt-4o",  # <-- CHANGE HERE
    # ...
)
```

---

## 📄 License

This project is licensed under the **MIT License**. See the `LICENSE` file for details.
