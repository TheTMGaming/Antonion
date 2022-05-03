from unittest.mock import MagicMock

import pytest
from telegram.ext import ConversationHandler

from app.internal.models.user import FriendRequest, TelegramUser
from app.internal.transport.bot.modules.friends.add_conversation import (
    _ALREADY_EXIST_ERROR,
    _REQUEST_ALREADY_EXIST_ERROR,
    _REQUEST_SUCCESS,
    _STUPID_CHOICE_SELF_ERROR,
    _USER_NOT_FOUND_ERROR,
    get_notification,
    handle_add_friend,
)
from app.internal.transport.bot.modules.friends.FriendStates import FriendStates


@pytest.mark.django_db
@pytest.mark.integration
def test_add_friend(
    update: MagicMock, context: MagicMock, telegram_user_with_phone: TelegramUser, another_telegram_user: TelegramUser
) -> None:
    update.message.text = str(another_telegram_user.id)
    next_state = handle_add_friend(update, context)

    update.message.reply_text.assert_called_once_with(_REQUEST_SUCCESS)
    context.bot.send_message.assert_called_once_with(
        chat_id=another_telegram_user.id, text=get_notification(telegram_user_with_phone)
    )
    assert next_state == ConversationHandler.END


@pytest.mark.django_db
@pytest.mark.integration
def test_add_friend__self(update: MagicMock, context: MagicMock, telegram_user_with_phone: TelegramUser) -> None:
    update.message.text = str(telegram_user_with_phone.id)
    _test_add_friend__error(update, context, _STUPID_CHOICE_SELF_ERROR)


@pytest.mark.django_db
@pytest.mark.integration
def test_add_friend__not_exist(update: MagicMock, context: MagicMock, telegram_user_with_phone: TelegramUser) -> None:
    update.message.text = "-1"
    _test_add_friend__error(update, context, _USER_NOT_FOUND_ERROR)


@pytest.mark.django_db
@pytest.mark.integration
def test_add_friend__already_exist_friend(
    update: MagicMock, context: MagicMock, telegram_user_with_phone: TelegramUser, friend: TelegramUser
) -> None:
    update.message.text = str(friend.id)
    _test_add_friend__error(update, context, _ALREADY_EXIST_ERROR)


@pytest.mark.django_db
@pytest.mark.integration
def test_add_friend__already_exist_request(
    update: MagicMock, context: MagicMock, telegram_user_with_phone: TelegramUser, another_telegram_user: TelegramUser
) -> None:
    update.message.text = str(another_telegram_user.id)
    FriendRequest.objects.create(source=telegram_user_with_phone, destination=another_telegram_user)

    _test_add_friend__error(update, context, _REQUEST_ALREADY_EXIST_ERROR)


def _test_add_friend__error(update: MagicMock, context: MagicMock, text: str) -> None:
    next_state = handle_add_friend(update, context)

    update.message.reply_text.assert_called_once_with(text)
    assert next_state == FriendStates.INPUT
