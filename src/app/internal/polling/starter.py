from django.conf import settings
from telegram.ext import Updater

from app.internal.bot import handlers


def start_polling() -> None:
    updater = Updater(settings.TELEGRAM_BOT_TOKEN)
    for handler in handlers:
        updater.dispatcher.add_handler(handler)

    updater.start_polling()
    updater.idle()
