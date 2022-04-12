from decimal import Decimal
from typing import Dict

from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

from app.internal.models.bank import BankAccount, BankObject
from app.internal.models.user import TelegramUser
from app.internal.services.bank import get_documents_with_enums, try_transfer
from app.internal.services.bank.service import parse_accrual
from app.internal.services.user import get_friends, get_user_info
from app.internal.transport.bot.document_details import send_documents_list
from app.internal.transport.bot.transfer.TransferStates import TransferStates

_STUPID_SOURCE = "У вас нет счёта или карты! Как вы собрались переводить?"
_STUPID_CHOICE = "ИнвАлидный выбор. Нет такого в списке! Введите заново, либо /cancel"

_FRIEND_VARIANTS_WELCOME = "Напишите номер друга, которому хотите перевести:\n\n"
_FRIEND_VARIANT = "{number}) {username} ({first_name})"

_TRANSFER_DESTINATION_WELCOME = "Выберите банковский счёт или карту получателя:\n"
_TRANSFER_SOURCE_WELCOME = "Откуда списать:\n"
_DOCUMENT_LIST_EMPTY = "К сожалению, у друга нет счетов и карт. Выберите другого, либо /cancel"
_INPUT_ACCRUAL_MESSAGE = "Введите размер перевода:\n"
_BALANCE_ZERO = "Баланс равен нулю. Выберите другой счёт или другую карту, либо /cancel"
_ACCRUAL_EMPTY_ERROR = "Размер платежа не может быть равняться 0. Введите значение больше 0, либо /cancel"
_ACCRUAL_GREATER_BALANCE_ERROR = (
    "Размер платежа не может быть больше, чем у вас имеется. Введите корректный размер, либо /cancel"
)

_TRANSFER_DETAILS = (
    "Проверьте корректность данных перевода. Если согласны, введите /confirm, иначе - /cancel\n\n"
    "Откуда ({source_type}): {source} ({balance})\n\n"
    "Куда ({dest_type}): {destination}\n\n"
    "Размер платежа: {accrual}\n\n"
)
_CARD_TYPE = "Карта"
_ACCOUNT_TYPE = "Счёт"
_TRANSFER_SUCCESS = "Ваш платёж успешно выполнен!"
_TRANSFER_FAIL = "Произошла непредвиденная ошибка!"

_SOURCE_DOCUMENTS_SESSION = "source_documents"
_DESTINATION_DOCUMENT_SESSION = "destination_document"
_SOURCE_DOCUMENT_SESSION = "source_document"
_FRIEND_VARIANTS_SESSION = "friend_variants"
_CHOSEN_FRIEND_SESSION = "chosen_friend"
_DESTINATION_DOCUMENTS_SESSION = "document_variants"
_DOCUMENT_CHOSEN_SESSION = "document"
_ACCRUAL_SESSION = "accrual"


def handle_transfer_start(update: Update, context: CallbackContext) -> int:
    user = get_user_info(update.effective_user.id)
    documents = get_documents_with_enums(user)

    if len(documents) == 0:
        update.message.reply_text(_STUPID_SOURCE)
        return ConversationHandler.END

    context.user_data[_SOURCE_DOCUMENTS_SESSION] = documents

    friends = dict((num, friend) for num, friend in enumerate(get_friends(user), 1))

    variants = "\n".join(
        _FRIEND_VARIANT.format(number=number, username=friend.username, first_name=friend.first_name)
        for number, friend in friends.items()
    )

    context.user_data[_FRIEND_VARIANTS_SESSION] = friends

    update.message.reply_text(_FRIEND_VARIANTS_WELCOME + variants)

    return TransferStates.DESTINATION


def handle_transfer_destination(update: Update, context: CallbackContext) -> int:
    number = int(update.message.text)
    friend: TelegramUser = context.user_data[_FRIEND_VARIANTS_SESSION].get(number)
    if not friend:
        update.message.reply_text(_STUPID_CHOICE)
        return TransferStates.DESTINATION

    context.user_data[_CHOSEN_FRIEND_SESSION] = friend

    documents = get_documents_with_enums(friend)

    if len(documents) == 0:
        update.message.reply_text(_DOCUMENT_LIST_EMPTY)
        return TransferStates.DESTINATION

    context.user_data[_DESTINATION_DOCUMENTS_SESSION] = documents

    send_documents_list(update, documents, _TRANSFER_DESTINATION_WELCOME)

    return TransferStates.DESTINATION_DOCUMENT


def handle_transfer_destination_document(update: Update, context: CallbackContext) -> int:
    number = int(update.message.text)
    destination: BankObject = context.user_data[_DESTINATION_DOCUMENTS_SESSION].get(number)

    if not destination:
        update.message.reply_text(_STUPID_CHOICE)
        return TransferStates.DESTINATION_DOCUMENT

    context.user_data[_DESTINATION_DOCUMENT_SESSION] = destination

    source_documents: Dict[str, BankObject] = context.user_data[_SOURCE_DOCUMENTS_SESSION]
    send_documents_list(update, source_documents, _TRANSFER_SOURCE_WELCOME, show_balance=True)

    return TransferStates.SOURCE_DOCUMENT


def handle_transfer_source_document(update: Update, context: CallbackContext) -> int:
    number = int(update.message.text)
    source: BankObject = context.user_data[_SOURCE_DOCUMENTS_SESSION].get(number)

    if not source:
        update.message.reply_text(_STUPID_CHOICE)
        return TransferStates.SOURCE_DOCUMENT

    if source.get_balance() == 0:
        update.message.reply_text(_BALANCE_ZERO)
        return TransferStates.SOURCE_DOCUMENT

    context.user_data[_SOURCE_DOCUMENT_SESSION] = source

    update.message.reply_text(_INPUT_ACCRUAL_MESSAGE)

    return TransferStates.ACCRUAL


def handle_transfer_accrual(update: Update, context: CallbackContext) -> int:
    accrual = parse_accrual(update.message.text)
    if accrual == 0:
        update.message.reply_text(_ACCRUAL_EMPTY_ERROR)
        return TransferStates.ACCRUAL

    source: BankObject = context.user_data[_SOURCE_DOCUMENT_SESSION]
    if accrual > source.get_balance():
        update.message.reply_text(_ACCRUAL_GREATER_BALANCE_ERROR)
        return TransferStates.ACCRUAL

    context.user_data[_ACCRUAL_SESSION] = accrual

    _send_transfer_details(update, context)

    return TransferStates.CONFIRM


def handle_transfer(update: Update, context: CallbackContext) -> int:
    source: BankObject = context.user_data[_SOURCE_DOCUMENT_SESSION]
    destination: BankObject = context.user_data[_DESTINATION_DOCUMENT_SESSION]
    accrual: Decimal = context.user_data[_ACCRUAL_SESSION]

    is_success = try_transfer(source, destination, accrual)
    message = _TRANSFER_SUCCESS if is_success else _TRANSFER_FAIL

    update.message.reply_text(message)

    return ConversationHandler.END


def _send_transfer_details(update: Update, context: CallbackContext) -> None:
    source: BankObject = context.user_data[_SOURCE_DOCUMENT_SESSION]
    destination: BankObject = context.user_data[_DESTINATION_DOCUMENT_SESSION]
    accrual: int = context.user_data[_ACCRUAL_SESSION]

    source_type = _ACCOUNT_TYPE if isinstance(source, BankAccount) else _CARD_TYPE
    dest_type = _ACCOUNT_TYPE if isinstance(destination, BankAccount) else _CARD_TYPE

    details = _TRANSFER_DETAILS.format(
        source=str(source),
        source_type=source_type,
        balance=source.get_balance(),
        destination=destination,
        dest_type=dest_type,
        accrual=accrual,
    )

    update.message.reply_text(details)
