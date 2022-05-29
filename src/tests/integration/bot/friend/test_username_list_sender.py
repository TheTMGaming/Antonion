from typing import List
from unittest.mock import MagicMock

import pytest

from app.internal.bot.modules.friends.FriendStates import FriendStates
from app.internal.bot.modules.friends.users_to_friends_sender import send_username_list
from app.internal.user.db.models import FriendRequest, TelegramUser
from tests.integration.bot.general import assert_conversation_end

_WELCOME = "abc"
_LIST_EMPTY = "ops"
_USERNAMES_SESSION = "usernames"


@pytest.mark.django_db
@pytest.mark.integration
def test_send_username_list(
    update: MagicMock,
    context: MagicMock,
    telegram_user_with_phone,
    another_telegram_users: List[TelegramUser],
) -> None:
    FriendRequest.objects.bulk_create(
        FriendRequest(source=user, destination=telegram_user_with_phone) for user in another_telegram_users
    )

    next_state = send_username_list(update, context, _LIST_EMPTY, _USERNAMES_SESSION, _WELCOME)

    assert next_state == FriendStates.INPUT
    assert _USERNAMES_SESSION in context.user_data
    assert type(context.user_data[_USERNAMES_SESSION]) is dict
    assert context.user_data[_USERNAMES_SESSION] == dict(
        (num, user.username) for num, user in enumerate(another_telegram_users, start=1)
    )


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
