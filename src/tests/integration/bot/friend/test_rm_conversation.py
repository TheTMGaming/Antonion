from typing import List

import pytest
from telegram import Update
from telegram.ext import CallbackContext

from app.internal.user.db.models import TelegramUser
from app.internal.user.presentation.handlers.bot.friends.rm_conversation import (
    _REMOVE_SUCCESS,
    _STUPID_CHOICE,
    _USER_SESSION,
    _USERNAMES_SESSION,
    FriendStates,
    get_notification,
    handle_rm_friend,
    handle_rm_friend_start,
)
from tests.integration.bot.conftest import assert_conversation_end, assert_conversation_start


@pytest.mark.django_db
@pytest.mark.integration
def test_rm_friend__start(
    update: Update, context: CallbackContext, telegram_user_with_phone: TelegramUser, friends: List[TelegramUser]
) -> None:
    next_state = handle_rm_friend_start(update, context)

    assert next_state == FriendStates.INPUT
    assert_conversation_start(context)
    assert _USERNAMES_SESSION in context.user_data
    assert _USER_SESSION in context.user_data
    assert type(context.user_data[_USERNAMES_SESSION]) is dict
    assert context.user_data[_USER_SESSION] == telegram_user_with_phone
    assert sorted(context.user_data[_USERNAMES_SESSION].values(), key=str) == sorted(friends, key=str)


@pytest.mark.django_db
@pytest.mark.integration
def test_rm_friend(
    update: Update, context: CallbackContext, telegram_user_with_phone: TelegramUser, friend: TelegramUser
) -> None:
    update.message.text = "1"
    context.user_data[_USER_SESSION] = telegram_user_with_phone
    context.user_data[_USERNAMES_SESSION] = {int(update.message.text): friend}

    next_state = handle_rm_friend(update, context)

    assert_conversation_end(next_state, context)
    assert not telegram_user_with_phone.friends.filter(id=friend.id).exists()
    assert not friend.friends.filter(id=telegram_user_with_phone.id).exists()
    update.message.reply_text.assert_called_once_with(_REMOVE_SUCCESS)
    context.bot.send_message.assert_called_once_with(chat_id=friend.id, text=get_notification(telegram_user_with_phone))


@pytest.mark.django_db
@pytest.mark.integration
def test_rm_friend__stupid_choice(
    update: Update, context: CallbackContext, telegram_user_with_phone: TelegramUser, friend: TelegramUser
) -> None:
    update.message.text = "-1"
    context.user_data[_USER_SESSION] = telegram_user_with_phone
    context.user_data[_USERNAMES_SESSION] = {1: friend}

    next_state = handle_rm_friend(update, context)

    assert next_state == FriendStates.INPUT
    assert telegram_user_with_phone.friends.filter(id=friend.id).exists()
    assert friend.friends.filter(id=telegram_user_with_phone.id).exists()
    update.message.reply_text.assert_called_once_with(_STUPID_CHOICE)
