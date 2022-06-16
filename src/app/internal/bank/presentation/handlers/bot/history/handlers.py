from django.utils.timezone import now
from telegram import Update
from telegram.ext import CallbackContext, CommandHandler, ConversationHandler, MessageHandler

from app.internal.bank.db.models import BankObject
from app.internal.bank.presentation.handlers.bot.document import send_document_list
from app.internal.bank.presentation.handlers.bot.history.HistoryStates import HistoryStates
from app.internal.general.bot.decorators import authorize_user, is_message_defined, is_not_user_in_conversation
from app.internal.general.bot.filters import INT
from app.internal.general.bot.handlers import cancel, mark_conversation_end, mark_conversation_start
from app.internal.general.services import bank_object_service, transaction_service, user_service

_WELCOME = "Выберите счёт или карту, либо /cancel:\n"
_STUPID_CHOICE = "Ммм. Я в банке работаю и то считать умею. Нет такого в списке! Повторите попытку, либо /cancel"
_LIST_EMPTY_MESSAGE = "Упс. Вы не завели ни карты, ни счёта. Позвоните Василию!"

_DOCUMENTS_SESSION = "documents"

_FILE_NAME = "Выписка для {number} к {date}.html"


@is_message_defined
@authorize_user()
@is_not_user_in_conversation
def handle_start(update: Update, context: CallbackContext) -> int:
    mark_conversation_start(context, entry_point.command)

    user = user_service.get_user(update.effective_user.id)

    documents = bank_object_service.get_documents_order(user)

    if not documents:
        update.message.reply_text(_LIST_EMPTY_MESSAGE)
        return mark_conversation_end(context)

    send_document_list(update, documents, _WELCOME)

    context.user_data[_DOCUMENTS_SESSION] = documents

    return HistoryStates.DOCUMENT


@is_message_defined
def handle_getting_document(update: Update, context: CallbackContext) -> int:
    document: BankObject = context.user_data[_DOCUMENTS_SESSION].get(int(update.message.text))

    if not document:
        update.message.reply_text(_STUPID_CHOICE)
        return HistoryStates.DOCUMENT

    account = bank_object_service.get_bank_account_from_document(document)
    content = transaction_service.get_history_html(account)

    update.message.reply_document(content, filename=_FILE_NAME.format(number=document.pretty_number, date=now().date()))

    return mark_conversation_end(context)


entry_point = CommandHandler("history", handle_start)


history_conversation = ConversationHandler(
    entry_points=[entry_point],
    states={
        HistoryStates.DOCUMENT: [MessageHandler(INT, handle_getting_document)],
    },
    fallbacks=[cancel],
)
