from telegram import Update
from telegram.ext import CallbackContext, CommandHandler

from app.internal.general.bot.decorators import (
    if_update_message_exists,
    if_user_is_created,
    if_user_is_not_in_conversation,
)
from app.internal.general.services import transaction_service, user_service

_TRANSACTION_DETAILS = (
    "Откуда: {source_number} ({source})\n"
    "Куда: {destination_number} ({destination})\n"
    "Размер: {accrual}\n"
    "Дата: {date}"
)
_NEW_TRANSACTIONS_EMPTY_MESSAGE = "Как жаль, новых платежей не было совершено. Банк желает, чтобы вы исправили ситуацию"
_LAST_END_MESSAGE = "Это был последний платёж..."


@if_update_message_exists
@if_user_is_created
@if_user_is_not_in_conversation
def handle_last(update: Update, context: CallbackContext) -> None:
    user = user_service.get_user(update.effective_user.id)
    transactions = transaction_service.get_and_mark_new_transactions(update.effective_user)

    if len(transactions) == 0:
        update.message.reply_text(_NEW_TRANSACTIONS_EMPTY_MESSAGE)
        return

    for transaction in transactions:
        source = "Вы" if transaction.source.owner == user else transaction.source.owner.username
        destination = "Вы" if transaction.destination.owner == user else transaction.destination.owner.username

        details = _TRANSACTION_DETAILS.format(
            source_number=transaction.source.short_number,
            source=source,
            destination_number=transaction.destination.short_number,
            destination=destination,
            accrual=transaction.accrual,
            date=transaction.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        )

        if transaction.photo:
            update.message.reply_photo(transaction.photo.open(), caption=details)
        else:
            update.message.reply_text(details)

    update.message.reply_text(_LAST_END_MESSAGE)


bank_commands = [CommandHandler("last", handle_last)]
