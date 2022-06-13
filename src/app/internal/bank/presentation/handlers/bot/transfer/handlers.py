from collections import namedtuple
from decimal import Decimal
from typing import Dict, Optional, Union

from django.conf import settings
from telegram import Document, File, PhotoSize, Update
from telegram.ext import CallbackContext, CommandHandler, ConversationHandler, MessageHandler

from app.internal.bank.db.models import BankAccount, BankCard, BankObject
from app.internal.bank.db.repositories import BankAccountRepository, BankCardRepository, TransactionRepository
from app.internal.bank.domain.services import BankObjectService, TransferService
from app.internal.bank.presentation.handlers.bot.document import send_document_list
from app.internal.bank.presentation.handlers.bot.transfer.TransferStates import TransferStates
from app.internal.general.bot.decorators import (
    if_phone_was_set,
    if_update_message_exists,
    if_user_exists,
    if_user_is_not_in_conversation,
)
from app.internal.general.bot.filters import FLOATING, IMAGE, INT
from app.internal.general.bot.handlers import cancel, mark_conversation_end, mark_conversation_start
from app.internal.user.db.models import TelegramUser
from app.internal.user.db.repositories import SecretKeyRepository, TelegramUserRepository
from app.internal.user.domain.services import FriendService, TelegramUserService

_STUPID_CHOICE_ERROR = "ИнвАлидный выбор. Нет такого в списке! Введите заново, либо /cancel"

_FRIEND_VARIANTS_WELCOME = "Напишите номер друга, которому хотите перевести:\n\n"
_FRIEND_VARIANT = "{number}) {username} ({first_name})"

_TRANSFER_DESTINATION_WELCOME = "Выберите банковский счёт или карту получателя:\n"
_TRANSFER_SOURCE_WELCOME = "Откуда списать:\n"
_ACCRUAL_WELCOME = "Введите размер перевода:\n"
_PHOTO_WELCOME = (
    f"Сделайте приятное другу, прикрепив картинку, либо /cancel или /skip."
    f" Только помни, максимальный размер картинки - {settings.MAX_SIZE_PHOTO_KB} KB"
)

_SOURCE_DOCUMENT_LIST_EMPTY_ERROR = "У вас нет счёта или карты! Как вы собрались переводить?"
_FRIEND_DOCUMENT_LIST_EMPTY_ERROR = "К сожалению, у друга нет счетов и карт. Выберите другого, либо /cancel"
_BALANCE_ZERO_ERROR = "Баланс равен нулю. Выберите другой счёт или другую карту, либо /cancel"
_ACCRUAL_PARSE_ERROR = "Размер перевода некорректен. Введите значение больше 0, либо /cancel"
_ACCRUAL_GREATER_BALANCE_ERROR = (
    "Размер перевода не может быть больше, чем у вас имеется. Введите корректный размер, либо /cancel"
)
_FRIEND_LIST_EMPTY_ERROR = "Заведите сначала друзей! Команда /add_friend"
_PHOTO_SIZE_ERROR = (
    f"Превышен максимальный размер - {settings.MAX_SIZE_PHOTO_KB} KB. Повторите попытку, либо /cancel или /skip"
)

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

_DESTINATION_SESSION = "destination_document"
_SOURCE_SESSION = "source_document"

_CHOSEN_FRIEND_SESSION = "chosen_friend"
_FRIEND_VARIANTS_SESSION = "friend_variants"
_ACCRUAL_SESSION = "accrual"
_CAPTION_SESSION = "photo_caption"
_PHOTO_SESSION = "transfer_photo"

Photo = namedtuple("Photo", ["id", "size"])


_friend_service = FriendService(friend_repo=TelegramUserRepository())
_user_service = TelegramUserService(user_repo=TelegramUserRepository(), secret_key_repo=SecretKeyRepository())
_bank_object_service = BankObjectService(account_repo=BankAccountRepository(), card_repo=BankCardRepository())
_transfer_service = TransferService(
    account_repo=BankAccountRepository(), card_repo=BankCardRepository(), transaction_repo=TransactionRepository()
)


@if_update_message_exists
@if_user_exists
@if_phone_was_set
@if_user_is_not_in_conversation
def handle_start(update: Update, context: CallbackContext) -> int:
    mark_conversation_start(context, entry_point.command)

    user = _user_service.get_user(update.effective_user.id)

    friends = _friend_service.get_friends_as_dict(user)
    if len(friends) == 0:
        update.message.reply_text(_FRIEND_LIST_EMPTY_ERROR)
        return mark_conversation_end(context)

    documents = _bank_object_service.get_documents_order(user)
    if len(documents) == 0:
        update.message.reply_text(_SOURCE_DOCUMENT_LIST_EMPTY_ERROR)
        return mark_conversation_end(context)

    context.user_data[_SOURCE_DOCUMENTS_SESSION] = documents

    _save_and_send_friend_list(update, context, friends)

    return TransferStates.DESTINATION


@if_update_message_exists
def handle_getting_destination(update: Update, context: CallbackContext) -> int:
    number = int(update.message.text)

    friend: TelegramUser = context.user_data[_FRIEND_VARIANTS_SESSION].get(number)
    if not friend:
        update.message.reply_text(_STUPID_CHOICE_ERROR)
        return TransferStates.DESTINATION

    context.user_data[_CHOSEN_FRIEND_SESSION] = friend

    documents = _bank_object_service.get_documents_order(friend)

    return _save_and_send_friend_document_list(update, context, documents)


@if_update_message_exists
def handle_getting_destination_document(update: Update, context: CallbackContext) -> int:
    number = int(update.message.text)
    destination: BankObject = context.user_data[_DESTINATION_DOCUMENTS_SESSION].get(number)

    if not destination:
        update.message.reply_text(_STUPID_CHOICE_ERROR)
        return TransferStates.DESTINATION_DOCUMENT

    context.user_data[_DESTINATION_SESSION] = _bank_object_service.get_bank_account_from_document(destination)

    source_documents: Dict[int, BankObject] = context.user_data[_SOURCE_DOCUMENTS_SESSION]
    send_document_list(update, source_documents, _TRANSFER_SOURCE_WELCOME, show_balance=True)

    return TransferStates.SOURCE_DOCUMENT


@if_update_message_exists
def handle_getting_source_document(update: Update, context: CallbackContext) -> int:
    number = int(update.message.text)
    source: BankObject = context.user_data[_SOURCE_DOCUMENTS_SESSION].get(number)

    if not source:
        update.message.reply_text(_STUPID_CHOICE_ERROR)
        return TransferStates.SOURCE_DOCUMENT

    source: BankAccount = _bank_object_service.get_bank_account_from_document(source)

    if _bank_object_service.is_balance_zero(source):
        update.message.reply_text(_BALANCE_ZERO_ERROR)
        return TransferStates.SOURCE_DOCUMENT

    context.user_data[_SOURCE_SESSION] = source

    update.message.reply_text(_ACCRUAL_WELCOME)

    return TransferStates.ACCRUAL


@if_update_message_exists
def handle_getting_accrual(update: Update, context: CallbackContext) -> int:
    try:
        accrual = _transfer_service.parse_accrual(update.message.text)
    except ValueError:
        update.message.reply_text(_ACCRUAL_PARSE_ERROR)
        return TransferStates.ACCRUAL

    source: BankAccount = context.user_data[_SOURCE_SESSION]
    if not _transfer_service.can_extract_from(source, accrual):
        update.message.reply_text(_ACCRUAL_GREATER_BALANCE_ERROR)
        return TransferStates.ACCRUAL

    context.user_data[_ACCRUAL_SESSION] = accrual

    update.message.reply_text(_PHOTO_WELCOME)

    return TransferStates.PHOTO


@if_update_message_exists
def handle_getting_photo(update: Update, context: CallbackContext) -> int:
    photo = update.message.photo[-1]

    if photo.file_size > settings.MAX_SIZE_PHOTO_BYTES:
        update.message.reply_text(_PHOTO_SIZE_ERROR)
        return TransferStates.PHOTO

    context.user_data[_PHOTO_SESSION] = photo

    _send_transfer_details(update, context)

    return TransferStates.CONFIRM


@if_update_message_exists
def handle_skip_getting_photo(update: Update, context: CallbackContext) -> int:
    _send_transfer_details(update, context)

    return TransferStates.CONFIRM


@if_update_message_exists
def handle_transfer(update: Update, context: CallbackContext) -> int:
    source: BankAccount = context.user_data[_SOURCE_SESSION]
    destination: BankAccount = context.user_data[_DESTINATION_SESSION]
    accrual: Decimal = context.user_data[_ACCRUAL_SESSION]
    photo: Optional[PhotoSize] = context.user_data.get(_PHOTO_SESSION)

    is_success = _transfer_service.try_transfer(source, destination, accrual, photo)
    message = _TRANSFER_SUCCESS if is_success else _TRANSFER_FAIL

    update.message.reply_text(message)

    if is_success:
        details = _get_accrual_detail(source, destination, accrual)
        destination_id = destination.get_owner().id

        if photo:
            context.bot.send_photo(chat_id=destination_id, photo=photo, caption=details)
        else:
            context.bot.send_message(chat_id=destination_id, text=details)

    return mark_conversation_end(context)


def _get_accrual_detail(source: BankObject, destination: BankObject, accrual: Decimal) -> str:
    type_ = _CARD_TYPE if isinstance(destination, BankCard) else _ACCOUNT_TYPE

    return _ACCRUAL_DETAILS.format(
        type=type_, number=destination.short_number, accrual=accrual, username=source.get_owner().username
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
    source: BankObject = context.user_data[_SOURCE_SESSION]
    destination: BankObject = context.user_data[_DESTINATION_SESSION]
    accrual: int = context.user_data[_ACCRUAL_SESSION]

    details = _TRANSFER_DETAILS.format(
        source=source.short_number,
        source_type=_type_to_string(source),
        balance=source.get_balance(),
        destination=destination,
        dest_type=_type_to_string(destination),
        accrual=accrual,
    )

    update.message.reply_text(details)


def _type_to_string(document: BankObject) -> str:
    return _ACCOUNT_TYPE if isinstance(document, BankAccount) else _CARD_TYPE


entry_point = CommandHandler("transfer", handle_start)


transfer_conversation = ConversationHandler(
    entry_points=[entry_point],
    states={
        TransferStates.DESTINATION: [MessageHandler(INT, handle_getting_destination)],
        TransferStates.DESTINATION_DOCUMENT: [MessageHandler(INT, handle_getting_destination_document)],
        TransferStates.SOURCE_DOCUMENT: [MessageHandler(INT, handle_getting_source_document)],
        TransferStates.ACCRUAL: [MessageHandler(FLOATING, handle_getting_accrual)],
        TransferStates.PHOTO: [
            MessageHandler(IMAGE, handle_getting_photo),
            CommandHandler("skip", handle_skip_getting_photo),
        ],
        TransferStates.CONFIRM: [CommandHandler("confirm", handle_transfer)],
    },
    fallbacks=[cancel],
)
