import pytest
from telegram import Update
from telegram.ext import CallbackContext

from app.internal.user.db.models import FriendRequest, TelegramUser
from app.internal.user.presentation.handlers.bot.friends.add_conversation import (
    _ALREADY_EXIST_ERROR,
    _REQUEST_ALREADY_EXIST_ERROR,
    _REQUEST_SUCCESS,
    _STUPID_CHOICE_SELF_ERROR,
    _USER_NOT_FOUND_ERROR,
    _WELCOME,
    FriendStates,
    get_notification,
    handle_add_friend,
    handle_add_friend_start,
)
from tests.integration.bot.conftest import assert_conversation_end, assert_conversation_start


@pytest.mark.django_db
@pytest.mark.integration
def test_add_friend_start(update: Update, context: CallbackContext, telegram_user_with_phone: TelegramUser) -> None:
    next_state = handle_add_friend_start(update, context)

    assert next_state == FriendStates.INPUT
    assert_conversation_start(context)
    update.message.reply_text.assert_called_once_with(_WELCOME)


@pytest.mark.django_db
@pytest.mark.integration
def test_add_friend(
    update: Update,
    context: CallbackContext,
    telegram_user_with_phone: TelegramUser,
    another_telegram_user: TelegramUser,
) -> None:
    update.message.text = str(another_telegram_user.id)
    next_state = handle_add_friend(update, context)

    assert_conversation_end(next_state, context)
    update.message.reply_text.assert_called_once_with(_REQUEST_SUCCESS)
    context.bot.send_message.assert_called_once_with(
        chat_id=another_telegram_user.id, text=get_notification(telegram_user_with_phone)
    )

    telegram_user_with_phone.refresh_from_db()
    assert FriendRequest.objects.filter(source=telegram_user_with_phone, destination=another_telegram_user).exists()
    assert not telegram_user_with_phone.friends.filter(id=another_telegram_user.id).exists()
    assert not another_telegram_user.friends.filter(id=telegram_user_with_phone.id).exists()


@pytest.mark.django_db
@pytest.mark.integration
def test_add_friend__self(update: Update, context: CallbackContext, telegram_user_with_phone: TelegramUser) -> None:
    update.message.text = str(telegram_user_with_phone.id)
    _test_add_friend__error(update, context, _STUPID_CHOICE_SELF_ERROR)


@pytest.mark.django_db
@pytest.mark.integration
def test_add_friend__not_exist(
    update: Update, context: CallbackContext, telegram_user_with_phone: TelegramUser
) -> None:
    update.message.text = "-1"
    _test_add_friend__error(update, context, _USER_NOT_FOUND_ERROR)


@pytest.mark.django_db
@pytest.mark.integration
def test_add_friend__already_exist_friend(
    update: Update, context: CallbackContext, telegram_user_with_phone: TelegramUser, friend: TelegramUser
) -> None:
    update.message.text = str(friend.id)
    _test_add_friend__error(update, context, _ALREADY_EXIST_ERROR)


@pytest.mark.django_db
@pytest.mark.integration
def test_add_friend__already_exist_request(
    update: Update, context: CallbackContext, telegram_user_with_phone, another_telegram_user: TelegramUser
) -> None:
    update.message.text = str(another_telegram_user.id)
    FriendRequest.objects.create(source=telegram_user_with_phone, destination=another_telegram_user)

    _test_add_friend__error(update, context, _REQUEST_ALREADY_EXIST_ERROR)


def _test_add_friend__error(update: Update, context: CallbackContext, text: str) -> None:
    next_state = handle_add_friend(update, context)

    assert next_state == FriendStates.INPUT
    update.message.reply_text.assert_called_once_with(text)
    context.bot.send_message.assert_not_called()
