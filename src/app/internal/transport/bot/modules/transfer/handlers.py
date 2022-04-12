from decimal import Decimal
from typing import Dict

from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

from app.internal.models.bank import BankAccount, BankObject
from app.internal.models.user import TelegramUser
from app.internal.services.bank.transfer import (
    can_extract_from,
    get_documents_with_enums,
    is_balance_zero,
    parse_accrual,
    try_transfer,
)
from app.internal.services.friend import get_friends_with_enums
from app.internal.services.user import get_user
from app.internal.transport.bot.modules.document import send_document_list
from app.internal.transport.bot.modules.transfer.TransferStates import TransferStates
from app.internal.transport.bot.modules.user.decorators import if_phone_is_set

_STUPID_CHOICE_ERROR = "ИнвАлидный выбор. Нет такого в списке! Введите заново, либо /cancel"

_FRIEND_VARIANTS_WELCOME = "Напишите номер друга, которому хотите перевести:\n\n"
_FRIEND_VARIANT = "{number}) {username} ({first_name})"

_TRANSFER_DESTINATION_WELCOME = "Выберите банковский счёт или карту получателя:\n"
_TRANSFER_SOURCE_WELCOME = "Откуда списать:\n"
_ACCRUAL_WELCOME = "Введите размер перевода:\n"

_SOURCE_DOCUMENT_LIST_EMPTY_ERROR = "У вас нет счёта или карты! Как вы собрались переводить?"
_FRIEND_DOCUMENT_LIST_EMPTY_ERROR = "К сожалению, у друга нет счетов и карт. Выберите другого, либо /cancel"
_BALANCE_ZERO_ERROR = "Баланс равен нулю. Выберите другой счёт или другую карту, либо /cancel"
_ACCRUAL_EMPTY_ERROR = "Размер перевода не может быть равняться 0. Введите значение больше 0, либо /cancel"
_ACCRUAL_GREATER_BALANCE_ERROR = (
    "Размер перевода не может быть больше, чем у вас имеется. Введите корректный размер, либо /cancel"
)
_FRIEND_LIST_EMPTY_ERROR = "Заведите сначала друзей! Команда /add_friend"

_TRANSFER_DETAILS = (
    "Проверьте корректность данных перевода. Если согласны, введите /confirm, иначе - /cancel\n\n"
    "Откуда ({source_type}): {source} ({balance})\n\n"
    "Куда ({dest_type}): {destination}\n\n"
    "Сумма: {accrual}\n\n"
)
_CARD_TYPE = "Карта"
_ACCOUNT_TYPE = "Счёт"
_TRANSFER_SUCCESS = "Ваш платёж успешно выполнен!"
_TRANSFER_FAIL = "Произошла непредвиденная ошибка!"


_SOURCE_DOCUMENTS_SESSION = "source_documents"
_DESTINATION_DOCUMENTS_SESSION = "destination_documents"

_DESTINATION_DOCUMENT_SESSION = "destination_document"
_SOURCE_DOCUMENT_SESSION = "source_document"

_CHOSEN_FRIEND_SESSION = "chosen_friend"
_DOCUMENT_CHOSEN_SESSION = "chosen_document"
_FRIEND_VARIANTS_SESSION = "friend_variants"
_ACCRUAL_SESSION = "accrual"


@if_phone_is_set
def handle_transfer_start(update: Update, context: CallbackContext) -> int:
    user = get_user(update.effective_user.id)

    friends = get_friends_with_enums(user)
    if len(friends) == 0:
        update.message.reply_text(_FRIEND_LIST_EMPTY_ERROR)
        return ConversationHandler.END

    documents = get_documents_with_enums(user)
    if len(documents) == 0:
        update.message.reply_text(_SOURCE_DOCUMENT_LIST_EMPTY_ERROR)
        return ConversationHandler.END

    context.user_data[_SOURCE_DOCUMENTS_SESSION] = documents

    _save_and_send_friend_list(update, context, friends)

    return TransferStates.DESTINATION


def handle_transfer_destination(update: Update, context: CallbackContext) -> int:
    number = int(update.message.text)
    friend: TelegramUser = context.user_data[_FRIEND_VARIANTS_SESSION].get(number)
    if not friend:
        update.message.reply_text(_STUPID_CHOICE_ERROR)
        return TransferStates.DESTINATION

    context.user_data[_CHOSEN_FRIEND_SESSION] = friend

    documents = get_documents_with_enums(friend)

    return _save_and_send_document_list(update, context, documents)


def handle_transfer_destination_document(update: Update, context: CallbackContext) -> int:
    number = int(update.message.text)
    destination: BankObject = context.user_data[_DESTINATION_DOCUMENTS_SESSION].get(number)

    if not destination:
        update.message.reply_text(_STUPID_CHOICE_ERROR)
        return TransferStates.DESTINATION_DOCUMENT

    context.user_data[_DESTINATION_DOCUMENT_SESSION] = destination

    source_documents: Dict[int, BankObject] = context.user_data[_SOURCE_DOCUMENTS_SESSION]
    send_document_list(update, source_documents, _TRANSFER_SOURCE_WELCOME, show_balance=True)

    return TransferStates.SOURCE_DOCUMENT


def handle_transfer_source_document(update: Update, context: CallbackContext) -> int:
    number = int(update.message.text)
    source: BankObject = context.user_data[_SOURCE_DOCUMENTS_SESSION].get(number)

    if not source:
        update.message.reply_text(_STUPID_CHOICE_ERROR)
        return TransferStates.SOURCE_DOCUMENT

    if is_balance_zero(source):
        update.message.reply_text(_BALANCE_ZERO_ERROR)
        return TransferStates.SOURCE_DOCUMENT

    context.user_data[_SOURCE_DOCUMENT_SESSION] = source

    update.message.reply_text(_ACCRUAL_WELCOME)

    return TransferStates.ACCRUAL


def handle_transfer_accrual(update: Update, context: CallbackContext) -> int:
    accrual = parse_accrual(update.message.text)
    if accrual == 0:
        update.message.reply_text(_ACCRUAL_EMPTY_ERROR)
        return TransferStates.ACCRUAL

    source: BankObject = context.user_data[_SOURCE_DOCUMENT_SESSION]
    if not can_extract_from(source, accrual):
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


def _save_and_send_friend_list(update: Update, context: CallbackContext, friends: Dict[int, TelegramUser]) -> None:
    context.user_data[_FRIEND_VARIANTS_SESSION] = friends

    friend_list = "\n".join(
        _FRIEND_VARIANT.format(number=number, username=friend.username, first_name=friend.first_name)
        for number, friend in friends.items()
    )

    update.message.reply_text(_FRIEND_VARIANTS_WELCOME + friend_list)


def _save_and_send_document_list(update: Update, context: CallbackContext, documents: Dict[int, BankObject]) -> int:
    if len(documents) == 0:
        update.message.reply_text(_FRIEND_DOCUMENT_LIST_EMPTY_ERROR)
        return TransferStates.DESTINATION

    context.user_data[_DESTINATION_DOCUMENTS_SESSION] = documents

    send_document_list(update, documents, _TRANSFER_DESTINATION_WELCOME)

    return TransferStates.DESTINATION_DOCUMENT


def _send_transfer_details(update: Update, context: CallbackContext) -> None:
    source: BankObject = context.user_data[_SOURCE_DOCUMENT_SESSION]
    destination: BankObject = context.user_data[_DESTINATION_DOCUMENT_SESSION]
    accrual: int = context.user_data[_ACCRUAL_SESSION]

    details = _TRANSFER_DETAILS.format(
        source=str(source),
        source_type=_type_to_string(source),
        balance=source.get_balance(),
        destination=destination,
        dest_type=_type_to_string(destination),
        accrual=accrual,
    )

    update.message.reply_text(details)


def _type_to_string(document: BankObject) -> str:
    return _ACCOUNT_TYPE if isinstance(document, BankAccount) else _CARD_TYPE
