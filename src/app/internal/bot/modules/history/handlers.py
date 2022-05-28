from telegram import Update
from telegram.ext import CallbackContext, CommandHandler, ConversationHandler, MessageHandler

from app.internal.bank.db.models import BankObject
from app.internal.bank.db.repositories import BankAccountRepository, BankCardRepository, TransactionRepository
from app.internal.bank.domain.services import BankObjectBotService, TransactionBotService
from app.internal.bot.decorators import (
    if_phone_is_set,
    if_update_message_exists,
    if_user_exist,
    if_user_is_not_in_conversation,
)
from app.internal.bot.modules.document import send_document_list
from app.internal.bot.modules.filters import INT
from app.internal.bot.modules.general import cancel, mark_conversation_end, mark_conversation_start
from app.internal.bot.modules.history.HistoryStates import HistoryStates
from app.internal.user.db.repositories import SecretKeyRepository, TelegramUserRepository
from app.internal.user.domain.services import TelegramUserService
from app.internal.utils.file_managers import create_temp_file, get_transfer_history_filename, remove_temp_file
from app.internal.utils.table_builders import build_transfer_history

_WELCOME = "Выберите счёт или карту:\n"
_STUPID_CHOICE = "Ммм. Я в банке работаю и то считать умею. Нет такого в списке! Повторите попытку, либо /cancel"
_LIST_EMPTY_MESSAGE = "Упс. Вы не завели ни карты, ни счёта. Позвоните Василию!"

_DOCUMENTS_SESSION = "documents"

_user_service = TelegramUserService(user_repo=TelegramUserRepository(), secret_key_repo=SecretKeyRepository())
_bank_object_service = BankObjectBotService(account_repo=BankAccountRepository(), card_repo=BankCardRepository())
_transaction_service = TransactionBotService(transaction_repo=TransactionRepository())


@if_update_message_exists
@if_user_exist
@if_phone_is_set
@if_user_is_not_in_conversation
def handle_start(update: Update, context: CallbackContext) -> int:
    mark_conversation_start(context, entry_point.command)

    user = _user_service.get_user(update.effective_user.id)

    documents = _bank_object_service.get_documents_order(user)

    if not documents:
        update.message.reply_text(_LIST_EMPTY_MESSAGE)
        return mark_conversation_end(context)

    send_document_list(update, documents, _WELCOME)

    context.user_data[_DOCUMENTS_SESSION] = documents

    return HistoryStates.DOCUMENT


@if_update_message_exists
def handle_getting_document(update: Update, context: CallbackContext) -> int:
    document: BankObject = context.user_data[_DOCUMENTS_SESSION].get(int(update.message.text))

    if not document:
        update.message.reply_text(_STUPID_CHOICE)
        return HistoryStates.DOCUMENT

    account = _bank_object_service.get_bank_account_from_document(document)
    transactions = _transaction_service.get_transactions(account)

    history = build_transfer_history(account, transactions)
    file = create_temp_file(history)

    update.message.reply_document(file, get_transfer_history_filename(document.pretty_number))

    remove_temp_file(file)

    return mark_conversation_end(context)


entry_point = CommandHandler("history", handle_start)


history_conversation = ConversationHandler(
    entry_points=[entry_point],
    states={
        HistoryStates.DOCUMENT: [MessageHandler(INT, handle_getting_document)],
    },
    fallbacks=[cancel],
)
