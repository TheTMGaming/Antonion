from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

from app.internal.models.bank import BankAccount, BankObject
from app.internal.services.bank.transfer import get_documents_with_enums
from app.internal.services.user import get_user
from app.internal.transport.bot.decorators import if_phone_is_set, if_update_message_exist, if_user_exist
from app.internal.transport.bot.modules.balance import BalanceStates
from app.internal.transport.bot.modules.document import send_document_list

_LIST_EMPTY_MESSAGE = "Упс. Вы не завели ни карты, ни счёта. Позвоните Василию!"
_WELCOME = "Выберите банковский счёт или карту, либо /cancel\n"
_STUPID_CHOICE = "Ммм. Я в банке работаю и то считать умею. Нет такого в списке! Повторите попытку, либо /cancel"

_BALANCE_BY_BANK_ACCOUNT = "На счёте {number} лежит {balance}"
_BALANCE_BY_CARD = "На карточке {number} лежит {balance}"

_DOCUMENTS_SESSION = "documents"


@if_update_message_exist
@if_user_exist
@if_phone_is_set
def handle_balance_start(update: Update, context: CallbackContext) -> int:
    user = get_user(update.effective_user.id)
    documents = get_documents_with_enums(user)

    if len(documents) == 0:
        update.message.reply_text(_LIST_EMPTY_MESSAGE)
        return ConversationHandler.END

    context.user_data[_DOCUMENTS_SESSION] = documents

    send_document_list(update, documents, _WELCOME)

    return BalanceStates.CHOICE


@if_update_message_exist
def handle_balance_choice(update: Update, context: CallbackContext) -> int:
    choice = int(update.message.text)
    document: BankObject = context.user_data[_DOCUMENTS_SESSION].get(choice)

    if not document:
        update.message.reply_text(_STUPID_CHOICE)
        return BalanceStates.CHOICE

    details = (_BALANCE_BY_BANK_ACCOUNT if isinstance(document, BankAccount) else _BALANCE_BY_CARD).format(
        number=document.pretty_number, balance=document.get_balance()
    )

    update.message.reply_text(details)

    return ConversationHandler.END
