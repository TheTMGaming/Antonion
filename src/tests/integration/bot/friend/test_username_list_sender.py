from typing import List
from unittest.mock import MagicMock

import pytest
from telegram import Update
from telegram.ext import CallbackContext

from app.internal.user.db.models import FriendRequest, TelegramUser
from app.internal.user.presentation.handlers.bot.friends.FriendStates import FriendStates
from app.internal.user.presentation.handlers.bot.friends.users_to_friends_sender import send_username_list

from tests.integration.bot.conftest import assert_conversation_end

_WELCOME = "abc"
_LIST_EMPTY = "ops"
_USERNAMES_SESSION = "usernames"


@pytest.mark.django_db
@pytest.mark.integration
def test_send_username_list(
    update: Update,
    context: CallbackContext,
    telegram_user_with_phone,
    another_telegram_users: List[TelegramUser],
    friend_requests: List[FriendRequest],
) -> None:
    next_state = send_username_list(update, context, _LIST_EMPTY, _USERNAMES_SESSION, _WELCOME)

    assert next_state == FriendStates.INPUT
    assert _USERNAMES_SESSION in context.user_data
    assert type(context.user_data[_USERNAMES_SESSION]) is dict

    username_dict: dict = context.user_data[_USERNAMES_SESSION]
    assert sorted(username_dict.keys()) == list(range(1, len(friend_requests) + 1))
    assert sorted(username_dict.values()) == sorted(map(lambda request: request.source.username, friend_requests))


@pytest.mark.django_db
@pytest.mark.integration
def test_send_username_list__empty(
    update: MagicMock,
    context: MagicMock,
    telegram_user_with_phone,
    another_telegram_users: List[TelegramUser],
) -> None:
    next_state = send_username_list(update, context, _LIST_EMPTY, _USERNAMES_SESSION, _WELCOME)

    assert_conversation_end(next_state, context)
    assert _USERNAMES_SESSION not in context.user_data
    update.message.reply_text.assert_called_once_with(_LIST_EMPTY)
