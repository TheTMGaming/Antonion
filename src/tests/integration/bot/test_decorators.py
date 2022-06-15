import pytest
from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

from app.internal.general.bot.decorators import (
    _UNDEFINED_PHONE,
    _UNDEFINED_USERNAME,
    _USER_DOESNT_EXIST,
    authorize_user,
    is_message_defined,
    is_not_user_in_conversation,
)
from app.internal.general.bot.handlers import mark_conversation_start
from app.internal.user.db.models import TelegramUser


@pytest.mark.integration
def test_is_message_defined(update: Update, context: CallbackContext) -> None:
    assert is_message_defined(_handler)(update, context) == _handler(update, context)


@pytest.mark.integration
def test_is_message_defined__none(update: Update, context: CallbackContext) -> None:
    update.message = None

    assert is_message_defined(_handler)(update, context) is None


@pytest.mark.django_db
@pytest.mark.integration
def test_authorizing_user(update: Update, context: CallbackContext, telegram_user_with_phone: TelegramUser) -> None:
    assert authorize_user()(_handler)(update, context) == _handler(update, context)


@pytest.mark.django_db
@pytest.mark.integration
def test_authorizing_user__uncreated_user(update: Update, context: CallbackContext) -> None:
    assert_authorizing_user__error(update, context, _USER_DOESNT_EXIST)


@pytest.mark.django_db
@pytest.mark.integration
def test_authorizing_user__undefined_username(
    update: Update, context: CallbackContext, telegram_user: TelegramUser
) -> None:
    update.effective_user.username = None

    assert_authorizing_user__error(update, context, _UNDEFINED_USERNAME)


@pytest.mark.django_db
@pytest.mark.integration
def test_authorizing_user__undefined_phone(
    update: Update, context: CallbackContext, telegram_user: TelegramUser
) -> None:
    assert_authorizing_user__error(update, context, _UNDEFINED_PHONE)


@pytest.mark.django_db
@pytest.mark.integration
def test_authorizing_user__ignoring_phone_if_defined(
    update: Update, context: CallbackContext, telegram_user: TelegramUser
) -> None:
    assert authorize_user(phone=False)(_handler)(update, context) == _handler(update, context)


@pytest.mark.django_db
@pytest.mark.integration
def test_authorizing_user__ignoring_phone_if_undefined(
    update: Update, context: CallbackContext, telegram_user_with_phone: TelegramUser
) -> None:
    assert authorize_user(phone=False)(_handler)(update, context) == _handler(update, context)


@pytest.mark.django_db
@pytest.mark.integration
def test_if_user_is_not_in_conversation(update: Update, context: CallbackContext, telegram_user: TelegramUser) -> None:
    assert is_not_user_in_conversation(_handler)(update, context) == _handler(update, context)


@pytest.mark.django_db
@pytest.mark.integration
def test_if_user_is_in_conversation(update: Update, context: CallbackContext, telegram_user: TelegramUser) -> None:
    mark_conversation_start(context, ["123"])

    assert is_not_user_in_conversation(_handler)(update, context) is None


def assert_authorizing_user__error(update: Update, context: CallbackContext, message: str) -> None:
    assert authorize_user()(_handler)(update, context) == ConversationHandler.END
    update.message.reply_text.assert_called_once_with(message)


def _handler(update: Update, context: CallbackContext) -> int:
    return 1
