from decimal import Decimal
from typing import Dict

from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

from app.internal.models.bank import BankAccount, BankCard, BankObject
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
from app.internal.transport.bot.decorators import if_phone_is_set, if_update_message_exist, if_user_exist
from app.internal.transport.bot.modules.document import send_document_list
from app.internal.transport.bot.modules.transfer.TransferStates import TransferStates

_STUPID_CHOICE_ERROR = "ИнвАлидный выбор. Нет такого в списке! Введите заново, либо /cancel"

_FRIEND_VARIANTS_WELCOME = "Напишите номер друга, которому хотите перевести:\n\n"
_FRIEND_VARIANT = "{number}) {username} ({first_name})"

_TRANSFER_DESTINATION_WELCOME = "Выберите банковский счёт или карту получателя:\n"
_TRANSFER_SOURCE_WELCOME = "Откуда списать:\n"
_ACCRUAL_WELCOME = "Введите размер перевода:\n"

_SOURCE_DOCUMENT_LIST_EMPTY_ERROR = "У вас нет счёта или карты! Как вы собрались переводить?"
_FRIEND_DOCUMENT_LIST_EMPTY_ERROR = "К сожалению, у друга нет счетов и карт. Выберите другого, либо /cancel"
_BALANCE_ZERO_ERROR = "Баланс равен нулю. Выберите другой счёт или другую карту, либо /cancel"
_ACCRUAL_PARSE_ERROR = "Размер перевода некорректен. Введите значение больше 0, либо /cancel"
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
_ACCRUAL_DETAILS = "{type} {number} зачислено {accrual} от {username}"

_CARD_TYPE = "Карта"
_ACCOUNT_TYPE = "Счёт"
_TRANSFER_SUCCESS = "Ваш платёж успешно выполнен!"
_TRANSFER_FAIL = "Произошла непредвиденная ошибка!"


_SOURCE_DOCUMENTS_SESSION = "source_documents"
_DESTINATION_DOCUMENTS_SESSION = "destination_documents"

_DESTINATION_DOCUMENT_SESSION = "destination_document"
_SOURCE_DOCUMENT_SESSION = "source_document"

_CHOSEN_FRIEND_SESSION = "chosen_friend"
_FRIEND_VARIANTS_SESSION = "friend_variants"
_ACCRUAL_SESSION = "accrual"


@if_update_message_exist
@if_user_exist
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


@if_update_message_exist
def handle_transfer_destination(update: Update, context: CallbackContext) -> int:
    number = int(update.message.text)
    friend: TelegramUser = context.user_data[_FRIEND_VARIANTS_SESSION].get(number)
    if not friend:
        update.message.reply_text(_STUPID_CHOICE_ERROR)
        return TransferStates.DESTINATION

    context.user_data[_CHOSEN_FRIEND_SESSION] = friend

    documents = get_documents_with_enums(friend)

    return _save_and_send_friend_document_list(update, context, documents)


@if_update_message_exist
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


@if_update_message_exist
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


@if_update_message_exist
def handle_transfer_accrual(update: Update, context: CallbackContext) -> int:
    try:
        accrual = parse_accrual(update.message.text)
    except ValueError:
        update.message.reply_text(_ACCRUAL_PARSE_ERROR)
        return TransferStates.ACCRUAL

    source: BankObject = context.user_data[_SOURCE_DOCUMENT_SESSION]
    if not can_extract_from(source, accrual):
        update.message.reply_text(_ACCRUAL_GREATER_BALANCE_ERROR)
        return TransferStates.ACCRUAL

    context.user_data[_ACCRUAL_SESSION] = accrual

    _send_transfer_details(update, context)

    return TransferStates.CONFIRM


@if_update_message_exist
def handle_transfer(update: Update, context: CallbackContext) -> int:
    source: BankObject = context.user_data[_SOURCE_DOCUMENT_SESSION]
    destination: BankObject = context.user_data[_DESTINATION_DOCUMENT_SESSION]
    accrual: Decimal = context.user_data[_ACCRUAL_SESSION]

    is_success = try_transfer(source, destination, accrual)
    message = _TRANSFER_SUCCESS if is_success else _TRANSFER_FAIL

    update.message.reply_text(message)
    context.bot.send_message(chat_id=destination.get_owner().id, text=_get_accrual_detail(source, destination, accrual))

    context.user_data.clear()

    return ConversationHandler.END


def _get_accrual_detail(source: BankObject, destination: BankObject, accrual: Decimal) -> str:
    type_ = _CARD_TYPE if isinstance(destination, BankCard) else _ACCOUNT_TYPE

    return _ACCRUAL_DETAILS.format(
        type=type_, number=destination.pretty_number, accrual=accrual, username=source.get_owner().username
    )


def _save_and_send_friend_list(update: Update, context: CallbackContext, friends: Dict[int, TelegramUser]) -> None:
    context.user_data[_FRIEND_VARIANTS_SESSION] = friends

    friend_list = "\n".join(
        _FRIEND_VARIANT.format(number=number, username=friend.username, first_name=friend.first_name)
        for number, friend in friends.items()
    )

    update.message.reply_text(_FRIEND_VARIANTS_WELCOME + friend_list)


def _save_and_send_friend_document_list(
    update: Update, context: CallbackContext, documents: Dict[int, BankObject]
) -> int:
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
