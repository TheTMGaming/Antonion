from itertools import chain
from typing import Callable

from django.conf import settings
from telegram.ext import CommandHandler, ConversationHandler, Filters, MessageHandler, Updater

from app.internal.transport.bot import (
    BalanceOperationStates,
    handle_confirmation_account,
    handle_confirmation_card,
    handle_getting_balance_by_account,
    handle_getting_balance_by_card,
    handle_me,
    handle_set_phone,
    handle_start,
)
from app.internal.transport.general_handlers import handle_cancel


def start() -> None:
    commands = [
        CommandHandler("start", handle_start),
        CommandHandler("set_phone", handle_set_phone),
        CommandHandler("me", handle_me),
    ]

    conversations = [
        _create_getting_balance_conversation("card_balance", handle_getting_balance_by_card, handle_confirmation_card),
        _create_getting_balance_conversation("balance", handle_getting_balance_by_account, handle_confirmation_account),
    ]

    updater = Updater(settings.TELEGRAM_BOT_TOKEN)
    for handler in chain(commands, conversations):
        updater.dispatcher.add_handler(handler)

    updater.start_polling()
    updater.idle()


def _create_getting_balance_conversation(
    entry_point_name: str, entry_point_handler: Callable, confirmation_handler: Callable
) -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler(entry_point_name, entry_point_handler)],
        states={
            BalanceOperationStates.CONFIRMATION: [MessageHandler(Filters.text & ~Filters.command, confirmation_handler)]
        },
        fallbacks=[CommandHandler("cancel", handle_cancel)],
    )
