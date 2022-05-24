from typing import List
from unittest.mock import MagicMock

import pytest

from app.internal.bot.modules.friends.commands import (
    _FRIENDSHIPS_EMPTY,
    _LIST_EMPTY_ERROR,
    handle_friends,
    handle_friendships,
)
from app.internal.models.user import TelegramUser


@pytest.mark.django_db
@pytest.mark.integration
def test_friends(update: MagicMock, context: MagicMock, telegram_users_with_phone, friends: List[TelegramUser]) -> None:
    handle_friends(update, context)

    assert update.message.reply_text.call_count == len(telegram_users_with_phone) - 1


@pytest.mark.django_db
@pytest.mark.integration
def test_friends__not_exist(update: MagicMock, context: MagicMock, telegram_users_with_phone) -> None:
    handle_friends(update, context)

    update.message.reply_text.assert_called_once_with(_LIST_EMPTY_ERROR)


@pytest.mark.django_db
@pytest.mark.integration
def test_friendships__empty(update: MagicMock, context: MagicMock, telegram_user_with_phone) -> None:
    handle_friendships(update, context)

    update.message.reply_text.assert_called_once_with(_FRIENDSHIPS_EMPTY)
