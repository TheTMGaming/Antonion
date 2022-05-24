import pytest
from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

from app.internal.bot.decorators import (
    _UNDEFINED_PHONE,
    _USER_DOESNT_EXIST,
    if_phone_is_set,
    if_update_message_exists,
    if_user_exist,
    if_user_is_not_in_conversation,
)
from app.internal.bot.modules.general import mark_conversation_start
from app.internal.users.db.models import TelegramUser


@pytest.mark.integration
def test_if_update_message_exist(update: Update, context: CallbackContext) -> None:
    assert if_update_message_exists(_handler)(update, context) == _handler(update, context)


@pytest.mark.integration
def test_if_update_message_exist_error(update: Update, context: CallbackContext) -> None:
    update.message = None

    assert if_update_message_exists(_handler)(update, context) is None


@pytest.mark.django_db
@pytest.mark.integration
def test_if_user_exist(update: Update, context: CallbackContext, telegram_user: TelegramUser) -> None:
    assert if_user_exist(_handler)(update, context) == _handler(update, context)


@pytest.mark.django_db
@pytest.mark.integration
def test_if_user_exist_error(update: Update, context: CallbackContext) -> None:
    assert if_user_exist(_handler)(update, context) == ConversationHandler.END
    update.message.reply_text.assert_called_once_with(_USER_DOESNT_EXIST)


@pytest.mark.django_db
@pytest.mark.integration
def test_if_phone_is_set(update: Update, context: CallbackContext, telegram_user_with_phone) -> None:
    assert if_phone_is_set(_handler)(update, context) == _handler(update, context)


@pytest.mark.django_db
@pytest.mark.integration
def test_if_phone_is_not_set(update: Update, context: CallbackContext, telegram_user: TelegramUser) -> None:
    assert if_phone_is_set(_handler)(update, context) == ConversationHandler.END
    update.message.reply_text.assert_called_once_with(_UNDEFINED_PHONE)


@pytest.mark.django_db
@pytest.mark.integration
def test_if_user_is_not_in_conversation(update: Update, context: CallbackContext, telegram_user: TelegramUser) -> None:
    assert if_user_is_not_in_conversation(_handler)(update, context) == _handler(update, context)


@pytest.mark.django_db
@pytest.mark.integration
def test_if_user_is_in_conversation(update: Update, context: CallbackContext, telegram_user: TelegramUser) -> None:
    mark_conversation_start(context, ["123"])

    assert if_user_is_not_in_conversation(_handler)(update, context) is None


def _handler(update: Update, context: CallbackContext) -> int:
    return 1
