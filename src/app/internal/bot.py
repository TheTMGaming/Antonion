from telegram.ext import Updater, CommandHandler
from config.settings import ENVIRON
from app.internal.transport.bot.handlers import *


def start():
    updater = Updater(ENVIRON('TELEGRAM_BOT_TOKEN'))
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', handle_start))
    dispatcher.add_handler(CommandHandler('set_phone', handle_set_phone))
    dispatcher.add_handler(CommandHandler('me', handle_me))

    updater.start_polling()
    updater.idle()
