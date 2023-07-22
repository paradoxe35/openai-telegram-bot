import io
import os
import logging
import env
import tempfile
from bot import createBotApplication, Update, MessageHandler, filters, ContextTypes, Voice
from audiotools import witai_transcribe, openai_transcribe


TRANSCRIBER_TYPE = os.environ.get("TRANSCRIBER_TYPE", "openai")
WIT_ACCESS_TOKEN = os.getenv("WIT_ACCESS_TOKEN")
OPENAI_API_TOKEN = os.getenv("OPENAI_API_TOKEN")


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


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text if update.message.text else ''
    if update.message.voice:
        text = await voice_to_text(update.message.voice)

    await update.message.reply_text("Response: " + text)


def main():
    application = createBotApplication()

    application.add_handler(MessageHandler(
        filters=filters.VOICE | filters.TEXT & filters.Regex(r"^(?!\/).*"),
        callback=message_handler
    ))

    application.run_polling(allowed_updates=[Update.MESSAGE])


if __name__ == '__main__':
    logger.info("Application started")
    main()
