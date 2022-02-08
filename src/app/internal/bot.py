from django.conf import settings

from app.internal.transport.bot.handlers import *

from telegram.ext import Updater, CommandHandler


def start() -> None:
    handlers = [
        CommandHandler('start', handle_start),
        CommandHandler('set_phone', handle_set_phone),
        CommandHandler('me', handle_me),
    ]

    updater = Updater(settings.TELEGRAM_BOT_TOKEN)

    for handler in handlers:
        updater.dispatcher.add_handler(handler)

    updater.start_polling()
    updater.idle()
