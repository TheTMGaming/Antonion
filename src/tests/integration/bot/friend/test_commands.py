from typing import List

import pytest
from telegram import Update
from telegram.ext import CallbackContext

from app.internal.user.db.models import TelegramUser
from app.internal.user.presentation.handlers.bot.friends.commands import (
    _FRIENDSHIPS_EMPTY,
    _LIST_EMPTY_ERROR,
    handle_friends,
    handle_friendships,
)


@pytest.mark.django_db
@pytest.mark.integration
def test_friends(
    update: Update, context: CallbackContext, friends: List[TelegramUser], telegram_user_with_phone: TelegramUser
) -> None:
    handle_friends(update, context)

    assert update.message.reply_text.call_count == len(friends)


@pytest.mark.django_db
@pytest.mark.integration
def test_friends__not_exist(update: Update, context: CallbackContext, telegram_user_with_phone: TelegramUser) -> None:
    handle_friends(update, context)

    update.message.reply_text.assert_called_once_with(_LIST_EMPTY_ERROR)


@pytest.mark.django_db
@pytest.mark.integration
def test_friendships__empty(update: Update, context: CallbackContext, telegram_user_with_phone: TelegramUser) -> None:
    handle_friendships(update, context)

    update.message.reply_text.assert_called_once_with(_FRIENDSHIPS_EMPTY)
