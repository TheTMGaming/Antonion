from django.conf import settings
from telegram.ext import Updater

from app.internal.transport.bot.starters.command_handlers import handlers


def start() -> None:
    updater = Updater(settings.TELEGRAM_BOT_TOKEN)
    for handler in handlers:
        updater.dispatcher.add_handler(handler)

    updater.start_polling()
    updater.idle()
