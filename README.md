# OpenAI Telegram Bot

## Overview

This is a Telegram chatbot powered by OpenAI's GPT-3, implemented in Python. It's designed to simulate conversations with a virtual girlfriend, providing a fun and interactive experience for users.

## Features

- Engage in natural and engaging conversations.
- Customize the bot's responses to fit your preferences.
- [Optional] Implement additional features or integrations to enhance the bot's capabilities.

## Getting Started

Follow these steps to get the Girlfriend OpenAI Telegram Bot up and running:

1. Clone the repository to your local machine:

   ```shell
   git clone https://github.com/your-username/girlfriend-openai-telegram-bot.git
   ```

2. Configure your Telegram Bot API token and OpenAI API credentials.

3. Install the necessary Python dependencies:

   ```shell
   pip install -r requirements.txt
   ```

4. Start the bot:

   ```shell
   python main.py
   ```

5. Open your Telegram app and start a conversation with your bot.

## Configuration

To configure the bot, you'll need to set the following environment variables:

- `TELEGRAM_BOT_TOKEN`: Your Telegram Bot API token.
- `OPENAI_API_KEY`: Your OpenAI API key.
- `WIT_ACCESS_TOKEN`: Your Wit AI API key.
- `ELEVENLABS_API_KEY`: Your Elevenlabs API key.
- `TRANSCRIBER_TYPE`: openai | witai
- `SYNTHESIZE_TYPE`: elevenlabs | witai

### OpenAI Memory
- `REDIS_URL="redis://localhost:6379/0"`

## Customization

You can customize the bot's behavior and responses by modifying the code in the `bot.py` file. Experiment with different conversation patterns, personalities, and responses to create your ideal virtual girlfriend.

