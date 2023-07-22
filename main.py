import os
import logging
from dotenv import load_dotenv
from bot import createBotApplication, Update, MessageHandler, filters, ContextTypes

load_dotenv()

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


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(update.message)
    await update.message.reply_text("Cool")


def main():
    application = createBotApplication()

    application.add_handler(MessageHandler(
        filters=filters.VOICE | filters.TEXT,
        callback=message_handler
    ))

    application.run_polling(allowed_updates=[Update.MESSAGE])


if __name__ == '__main__':
    logger.info("Application started")
    main()
