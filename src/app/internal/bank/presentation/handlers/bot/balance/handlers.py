from telegram import Update
from telegram.ext import CallbackContext, CommandHandler, ConversationHandler, MessageHandler

from app.internal.bank.db.models import BankAccount, BankObject
from app.internal.bank.presentation.handlers.bot.balance.BalanceStates import BalanceStates
from app.internal.bank.presentation.handlers.bot.document import send_document_list
from app.internal.general.bot.decorators import (
    if_update_message_exists,
    if_user_is_created,
    if_user_is_not_in_conversation,
)
from app.internal.general.bot.filters import INT
from app.internal.general.bot.handlers import cancel, mark_conversation_end, mark_conversation_start
from app.internal.general.services import bank_object_service, user_service

_LIST_EMPTY_MESSAGE = "Упс. Вы не завели ни карты, ни счёта. Позвоните Василию!"
_WELCOME = "Выберите банковский счёт или карту, либо /cancel\n"
_STUPID_CHOICE = "Ммм. Я в банке работаю и то считать умею. Нет такого в списке! Повторите попытку, либо /cancel"

_BALANCE_BY_BANK_ACCOUNT = "На счёте {number} лежит {balance}"
_BALANCE_BY_CARD = "На карточке {number} лежит {balance}"

_DOCUMENTS_SESSION = "documents"


@if_update_message_exists
@if_user_is_created
@if_user_is_not_in_conversation
def handle_start(update: Update, context: CallbackContext) -> int:
    mark_conversation_start(context, entry_point.command)

    user = user_service.get_user(update.effective_user.id)
    documents = bank_object_service.get_documents_order(user)

    if len(documents) == 0:
        update.message.reply_text(_LIST_EMPTY_MESSAGE)
        return mark_conversation_end(context)

    context.user_data[_DOCUMENTS_SESSION] = documents

    send_document_list(update, documents, _WELCOME)

    return BalanceStates.CHOICE


@if_update_message_exists
def handle_choice(update: Update, context: CallbackContext) -> int:
    choice = int(update.message.text)
    document: BankObject = context.user_data[_DOCUMENTS_SESSION].get(choice)

    if not document:
        update.message.reply_text(_STUPID_CHOICE)
        return BalanceStates.CHOICE

    details = (_BALANCE_BY_BANK_ACCOUNT if isinstance(document, BankAccount) else _BALANCE_BY_CARD).format(
        number=document.short_number, balance=document.get_balance()
    )

    update.message.reply_text(details)

    return mark_conversation_end(context)


entry_point = CommandHandler("balance", handle_start)


balance_conversation = ConversationHandler(
    entry_points=[entry_point],
    states={
        BalanceStates.CHOICE: [MessageHandler(INT, handle_choice)],
    },
    fallbacks=[cancel],
)
