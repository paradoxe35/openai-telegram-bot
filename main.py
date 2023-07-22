import io
import os
import logging
from dotenv import load_dotenv
import tempfile
from telegram import Update, Voice, constants
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


async def voice_to_text(voice: Voice):
    text = ""
    file = await voice.get_file()
    tmpaudio = tempfile.NamedTemporaryFile(suffix=".ogg")
    await file.download_to_drive(tmpaudio.name)

    # Transcribe
    try:
        if TRANSCRIBER_TYPE != "openai":
            raise Exception("Wit.AI Fallback TRANSCRIBER")

        resutl = openai_transcribe(tmpaudio, OPENAI_API_TOKEN)
        text += resutl
    except Exception as e:
        # Wit AI (as Fallback)
        resutl = witai_transcribe(
            file=tmpaudio,
            api_key=WIT_ACCESS_TOKEN
        )
        for speech in resutl:
            text += speech
    finally:
        tmpaudio.close()

    return text


async def reply_message(update: Update, text: str):
    file = None

    try:
        if SYNTHESIZE_TYPE != "elevenlabs":
            raise Exception("Wit.AI Fallback SYNTHESIZE")

        file = elevenlabs_synthesize(text, ELEVENLABS_API_KEY)
        await update.message.reply_audio(file.file, caption=text)
    except Exception as e:
        chuncked_message = chunk_text_message(text)
        for chunk in chuncked_message:
            file = witai_synthesize(chunk, WIT_ACCESS_TOKEN)
            await update.message.reply_audio(file.file, caption=chunk)

    finally:
        if file:
            file.close()


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_chat_action(constants.ChatAction.RECORD_VOICE)
    text = update.message.text if update.message.text else ''

    if update.message.voice:
        text = await voice_to_text(update.message.voice)

    await reply_message(update, text)


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
