import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters


def createBotApplication():
    return ApplicationBuilder().token(
        os.getenv("TELEGRAM_BOT_TOKEN")
    ).build()