from unittest.mock import MagicMock

import pytest
from telegram.ext import ConversationHandler

from app.internal.models.user import TelegramUser
from app.internal.transport.bot.decorators import (
    _UNDEFINED_PHONE,
    _USER_DOESNT_EXIST,
    if_phone_is_set,
    if_update_message_exist,
    if_user_exist,
    if_user_is_not_in_conversation,
)
from app.internal.transport.bot.modules.general import mark_conversation_start


@pytest.mark.integration
def test_if_update_message_exist(update: MagicMock, context: MagicMock) -> None:
    assert if_update_message_exist(_handler)(update, context) == _handler(update, context)


@pytest.mark.integration
def test_if_update_message_exist_error(update: MagicMock, context: MagicMock) -> None:
    update.message = None

    assert if_update_message_exist(_handler)(update, context) is None


@pytest.mark.django_db
@pytest.mark.integration
def test_if_user_exist(update: MagicMock, context: MagicMock, telegram_user: TelegramUser) -> None:
    assert if_user_exist(_handler)(update, context) == _handler(update, context)


@pytest.mark.django_db
@pytest.mark.integration
def test_if_user_exist_error(update: MagicMock, context: MagicMock) -> None:
    assert if_user_exist(_handler)(update, context) == ConversationHandler.END
    update.message.reply_text.assert_called_once_with(_USER_DOESNT_EXIST)


@pytest.mark.django_db
@pytest.mark.integration
def test_if_phone_is_set(update: MagicMock, context: MagicMock, telegram_user_with_phone: TelegramUser) -> None:
    assert if_phone_is_set(_handler)(update, context) == _handler(update, context)


@pytest.mark.django_db
@pytest.mark.integration
def test_if_phone_is_not_set(update: MagicMock, context: MagicMock, telegram_user: TelegramUser) -> None:
    assert if_phone_is_set(_handler)(update, context) == ConversationHandler.END
    update.message.reply_text.assert_called_once_with(_UNDEFINED_PHONE)


@pytest.mark.django_db
@pytest.mark.integration
def test_if_user_is_not_in_conversation(update: MagicMock, context: MagicMock, telegram_user: TelegramUser) -> None:
    assert if_user_is_not_in_conversation(_handler)(update, context) == _handler(update, context)


@pytest.mark.django_db
@pytest.mark.integration
def test_if_user_is_in_conversation(update: MagicMock, context: MagicMock, telegram_user: TelegramUser) -> None:
    mark_conversation_start(context, ["123"])

    assert if_user_is_not_in_conversation(_handler)(update, context) is None


def _handler(update: MagicMock, context: MagicMock) -> int:
    return 1
