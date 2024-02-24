import os
from telegram import Bot
from telegram import Update


def init_tracker_chat():
    bot_token = os.environ.get("TRACKER_BOT_TOKEN")
    bot_chat_id = os.environ.get("TRACKER_BOT_CHAT_ID")
    chat_id = os.environ.get("TRACKER_CHAT_ID")

    if not bot_token or not bot_chat_id or not chat_id:
        return None

    bot = Bot(token=bot_token)

    async def send_track_message(
        update: Update,
        message: str | None = None,
        reply: str | None = None,
    ):
        if str(update.message.chat_id) != chat_id:
            return

        if message:
            username = update.effective_user.full_name or update.effective_user.username
            message_text = f"{username}\n\n{message}"
            await bot.sendMessage(
                chat_id=int(bot_chat_id),
                text=message_text,
            )

        if reply:
            message_text = f"AI Bot\n\n{reply}\n\n----------------"
            await bot.sendMessage(
                chat_id=int(bot_chat_id),
                text=message_text,
            )

    return send_track_message
