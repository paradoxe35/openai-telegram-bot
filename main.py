import asyncio
import os
import logging
import tempfile

from chatgpt_md_converter import telegram_format
from dotenv import load_dotenv
from telegram import Update, Voice, constants
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from audiotools import (
    witai_transcribe,
    openai_transcribe,
    witai_synthesize,
    elevenlabs_synthesize,
)
from chat import init_llm_chain
from tracker import init_tracker_chat

load_dotenv()

TRANSCRIBER_TYPE = os.environ.get("TRANSCRIBER_TYPE", "openai")
SYNTHESIZE_TYPE = os.environ.get("SYNTHESIZE_TYPE", "elevenlabs")
CHATGPT_API_MODEL = os.environ.get("CHATGPT_API_MODEL", None)

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
WIT_ACCESS_TOKEN = os.getenv("WIT_ACCESS_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


predict = init_llm_chain(
    openai_api_key=OPENAI_API_KEY,
    model_name=CHATGPT_API_MODEL,
)

send_track_message = init_tracker_chat()


# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


async def voice_to_text(voice: Voice):
    text = ""
    file = await voice.get_file()
    tmp_audio = tempfile.NamedTemporaryFile(suffix=".ogg")
    await file.download_to_drive(tmp_audio.name)

    # Transcribe
    try:
        if TRANSCRIBER_TYPE != "openai":
            raise Exception("Wit.AI Fallback TRANSCRIBER")

        result = openai_transcribe(tmp_audio, OPENAI_API_KEY)
        text += result
    except Exception as _:
        # Wit AI (as Fallback)
        result = witai_transcribe(file=tmp_audio, api_key=WIT_ACCESS_TOKEN)
        for speech in result:
            text += speech
    finally:
        tmp_audio.close()

    return text


async def reply_audio_message(update: Update, text: str):
    file = None

    try:
        if SYNTHESIZE_TYPE != "elevenlabs":
            raise Exception("Wit.AI Fallback SYNTHESIZE")

        file = elevenlabs_synthesize(text, ELEVENLABS_API_KEY)
        await update.message.reply_audio(file.file, caption=text)
    except Exception as _:
        file = witai_synthesize(text, WIT_ACCESS_TOKEN)
        await update.message.reply_audio(file.file, caption=text)

    finally:
        if file:
            file.close()


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text if update.message.text else ""

    # Tracker Message
    if send_track_message:
        asyncio.create_task(send_track_message(update=update, message=text))

    if update.message.voice:
        await update.message.reply_chat_action(constants.ChatAction.RECORD_VOICE)
        text = await voice_to_text(update.message.voice)
    else:
        await update.message.reply_chat_action(constants.ChatAction.TYPING)

    reply = predict(text, update.message.chat_id)
    formattedReply = telegram_format(reply)

    if update.message.voice:
        await reply_audio_message(update, reply)
    else:
        await update.message.reply_text(
            formattedReply,
            parse_mode=constants.ParseMode.HTML,
        )

    # Tracker Reply
    if send_track_message:
        asyncio.create_task(send_track_message(update=update, reply=reply))


def main():
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(
        MessageHandler(
            filters=(filters.VOICE | filters.TEXT & filters.Regex(r"^(?!\/).*"))
            & filters.ChatType.PRIVATE,
            callback=message_handler,
        )
    )

    application.run_polling(allowed_updates=[Update.MESSAGE])


if __name__ == "__main__":
    logger.info("Application started")
    main()
