from typing import List
from unittest.mock import MagicMock

import pytest
from telegram.ext import ConversationHandler

from app.internal.models.user import TelegramUser
from app.internal.transport.bot.modules.friends.FriendStates import FriendStates
from app.internal.transport.bot.modules.friends.rm_conversation import (
    _REMOVE_SUCCESS,
    get_notification,
    handle_rm_friend, handle_rm_friend_start, _USERNAMES_SESSION, _USER_SESSION, _STUPID_CHOICE, _REMOVE_ERROR,
)


@pytest.mark.django_db
@pytest.mark.integration
def test_rm_friend__start(update: MagicMock, context: MagicMock, telegram_user_with_phone: TelegramUser, friends: List[TelegramUser]) -> None:
    next_state = handle_rm_friend_start(update, context)

    assert next_state == FriendStates.INPUT
    assert _USERNAMES_SESSION in context.user_data
    assert _USER_SESSION in context.user_data
    assert type(context.user_data[_USERNAMES_SESSION]) is dict
    assert context.user_data[_USER_SESSION] == telegram_user_with_phone
    assert sorted(context.user_data[_USERNAMES_SESSION].values(), key=str) == sorted(friends, key=str)


@pytest.mark.django_db
@pytest.mark.integration
def test_rm_friend(
    update: MagicMock, context: MagicMock, telegram_user_with_phone: TelegramUser, friend: TelegramUser
) -> None:
    update.message.text = "1"
    context.user_data[_USER_SESSION] = telegram_user_with_phone
    context.user_data[_USERNAMES_SESSION] = {int(update.message.text): friend}

    next_state = handle_rm_friend(update, context)

    assert next_state == ConversationHandler.END
    assert not telegram_user_with_phone.friends.filter(id=friend.id).exists()
    assert not friend.friends.filter(id=telegram_user_with_phone.id).exists()
    update.message.reply_text.assert_called_once_with(_REMOVE_SUCCESS)
    context.bot.send_message.assert_called_once_with(chat_id=friend.id, text=get_notification(telegram_user_with_phone))
    assert len(context.user_data) == 0


@pytest.mark.django_db
@pytest.mark.integration
def test_rm_friend__stupid_choice(
    update: MagicMock, context: MagicMock, telegram_user_with_phone: TelegramUser, friend: TelegramUser
) -> None:
    update.message.text = "-1"
    context.user_data[_USER_SESSION] = telegram_user_with_phone
    context.user_data[_USERNAMES_SESSION] = {1: friend}

    next_state = handle_rm_friend(update, context)

    assert next_state == FriendStates.INPUT
    assert telegram_user_with_phone.friends.filter(id=friend.id).exists()
    assert friend.friends.filter(id=telegram_user_with_phone.id).exists()
    update.message.reply_text.assert_called_once_with(_STUPID_CHOICE)
