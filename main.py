import io
import os
import logging
from dotenv import load_dotenv
import tempfile
from telegram import Update, Voice
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from audiotools import witai_transcribe, openai_transcribe, witai_synthesize, elevenlabs_synthesize

load_dotenv()

TRANSCRIBER_TYPE = os.environ.get("TRANSCRIBER_TYPE", "openai")
SYNTHESIZE_TYPE = os.environ.get("SYNTHESIZE_TYPE", "elevenlabs")

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
WIT_ACCESS_TOKEN = os.getenv("WIT_ACCESS_TOKEN")
OPENAI_API_TOKEN = os.getenv("OPENAI_API_TOKEN")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


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
    tmpaudio = tempfile.NamedTemporaryFile(suffix=".ogg")
    await file.download_to_drive(tmpaudio.name)

    # Transcribe
    if TRANSCRIBER_TYPE == "openai":
        resutl = openai_transcribe(tmpaudio, OPENAI_API_TOKEN)
        text += resutl
    else:
        # Wit AI
        resutl = witai_transcribe(
            file=tmpaudio,
            api_key=WIT_ACCESS_TOKEN
        )

        for speech in resutl:
            text += speech

    tmpaudio.close()
    return text


def chunk_text_message(text: str):
    messages = []
    message = ""
    chunks = text.split(" ")

    for chunk in chunks:
        if len(message) + len(chunk) > 280:
            messages.append(message)
            message = ""
        message += f" {chunk}" if len(message) > 0 else chunk

    messages.append(message)

    return messages


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text if update.message.text else ''

    if update.message.voice:
        text = await voice_to_text(update.message.voice)

    chuncked_message = chunk_text_message(text)

    if SYNTHESIZE_TYPE == "elevenlabs":
        file = elevenlabs_synthesize(text, ELEVENLABS_API_KEY)
        try:
            await update.message.reply_audio(file.file, caption=text)
        finally:
            file.close()
    else:
        # Wit AI
        for chunk in chuncked_message:
            file = witai_synthesize(chunk, WIT_ACCESS_TOKEN)
            try:
                await update.message.reply_audio(file.file, caption=chunk)
            finally:
                file.close()


def main():
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(MessageHandler(
        filters=filters.VOICE | filters.TEXT & filters.Regex(r"^(?!\/).*"),
        callback=message_handler
    ))

    application.run_polling(allowed_updates=[Update.MESSAGE])


if __name__ == '__main__':
    logger.info("Application started")
    main()
