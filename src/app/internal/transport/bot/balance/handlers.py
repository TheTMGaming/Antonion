from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

from app.internal.models.bank import BankAccount, BankObject
from app.internal.services.bank import get_documents_with_enums
from app.internal.services.user import get_user_info
from app.internal.transport.bot.balance import BalanceStates
from app.internal.transport.bot.document_details import send_documents_list

_LIST_EMPTY_MESSAGE = "Упс. Вы не завели ни карты, ни счёта. Позвоните Василию!"
_WELCOME = "Выберите банковский счёт или карту, либо /cancel\n"
_STUPID_CHOICE = "Ммм. Я в банке работаю и то считать умею. Нет такого в списке! Повторите попытку, либо /cancel"

_BALANCE_BY_BANK_ACCOUNT = "На счёте {number} лежит {balance}"
_BALANCE_BY_CARD = "На карточке {number} лежит {balance}"

_DOCUMENTS_SESSION = "documents"


def handle_balance_start(update: Update, context: CallbackContext) -> int:
    user = get_user_info(update.effective_user.id)
    documents = get_documents_with_enums(user)

    context.user_data[_DOCUMENTS_SESSION] = documents

    send_documents_list(update, documents, _WELCOME)

    return BalanceStates.CHOICE


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
