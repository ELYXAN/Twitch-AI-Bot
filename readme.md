# 🤖 Twitch AI Chatbot via Channel Points

A Python bot that connects to your Twitch chat, listens for a specific channel point reward, and uses the OpenAI API (e.g., GPT-4o) to answer user prompts directly in chat.

![Bot Demo GIF](https://user-images.githubusercontent.com/12345/your-demo-image-link.gif)
*(Tip: Create a short GIF showing the bot in action and replace the link above to showcase your project.)*

---

## ✨ Features

* **Channel Point Integration:** Triggers only on a custom channel point reward that you specify.
* **OpenAI API Integration:** Leverages modern language models like `gpt-4o` or `gpt-3.5-turbo` to generate intelligent responses.
* **Automatic Token Refresh:** Uses a secure refresh token mechanism to automatically and safely authenticate with Twitch on every startup. No more manual password updates.
* **Customizable Personality:** The system prompt can be easily modified to give the bot a unique personality.
* **Simple Configuration:** All important settings are collected at the top of the script for easy access.

---

## 🛠️ Setup & Installation

Follow these steps to get the bot running for your channel.

### 1. Clone the Repository

Clone this repository to your local machine:
```bash
git clone [https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git](https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git)
cd YOUR_REPO_NAME
