from telegram import Update
from telegram.ext import CallbackContext, CommandHandler, ConversationHandler, MessageHandler

from app.internal.models.bank import BankObject
from app.internal.services.bank.account import get_bank_account_from_document
from app.internal.services.bank.transaction import get_transactions
from app.internal.services.bank.transfer import get_documents_with_enums
from app.internal.services.user import get_user
from app.internal.services.utils import (
    build_transfer_history,
    create_temp_file,
    get_transfer_history_filename,
    remove_temp_file,
)
from app.internal.transport.bot.decorators import if_phone_is_set, if_update_message_exist, if_user_exist
from app.internal.transport.bot.modules.cancel import cancel
from app.internal.transport.bot.modules.document import send_document_list
from app.internal.transport.bot.modules.filters import INT
from app.internal.transport.bot.modules.history.HistoryStates import HistoryStates

_WELCOME = "Выберите счёт или карту:\n"
_STUPID_CHOICE = "Ммм. Я в банке работаю и то считать умею. Нет такого в списке! Повторите попытку, либо /cancel"
_LIST_EMPTY_MESSAGE = "Упс. Вы не завели ни карты, ни счёта. Позвоните Василию!"

_DOCUMENTS_SESSION = "documents"


@if_update_message_exist
@if_user_exist
@if_phone_is_set
def handle_history_start(update: Update, context: CallbackContext) -> int:
    user = get_user(update.effective_user.id)

    documents = get_documents_with_enums(user)

    if not documents:
        update.message.reply_text(_LIST_EMPTY_MESSAGE)
        return ConversationHandler.END

    send_document_list(update, documents, _WELCOME)

    context.user_data[_DOCUMENTS_SESSION] = documents

    return HistoryStates.DOCUMENT


@if_update_message_exist
def handle_history_document(update: Update, context: CallbackContext) -> int:
    document: BankObject = context.user_data[_DOCUMENTS_SESSION].get(int(update.message.text))

    if not document:
        update.message.reply_text(_STUPID_CHOICE)
        return HistoryStates.DOCUMENT

    account = get_bank_account_from_document(document)
    transactions = get_transactions(account)

    history = build_transfer_history(account, transactions)
    file = create_temp_file(history)

    update.message.reply_document(file, get_transfer_history_filename(document.pretty_number))

    remove_temp_file(file)

    return ConversationHandler.END


history_conversation = ConversationHandler(
    entry_points=[CommandHandler("history", handle_history_start)],
    states={
        HistoryStates.DOCUMENT: [MessageHandler(INT, handle_history_document)],
    },
    fallbacks=[cancel],
)
