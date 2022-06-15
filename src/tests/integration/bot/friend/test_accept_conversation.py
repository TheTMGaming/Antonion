import pytest
from telegram import Update
from telegram.ext import CallbackContext

from app.internal.user.db.models import FriendRequest, TelegramUser
from app.internal.user.presentation.handlers.bot.friends.accept_conversation import (
    _FRIEND_CANCEL,
    _STUPID_CHOICE,
    _USERNAMES_SESSION,
    get_notification,
    handle_accept,
    handle_accept_start,
)
from app.internal.user.presentation.handlers.bot.friends.FriendStates import FriendStates
from tests.integration.bot.conftest import assert_conversation_end, assert_conversation_start


@pytest.mark.django_db
@pytest.mark.integration
def test_accept_start(
    update: Update,
    context: CallbackContext,
    telegram_user_with_phone: TelegramUser,
    another_telegram_user: TelegramUser,
) -> None:
    FriendRequest.objects.create(source=another_telegram_user, destination=telegram_user_with_phone)

    next_state = handle_accept_start(update, context)

    assert next_state == FriendStates.INPUT
    assert_conversation_start(context)
    assert context.user_data.get(_USERNAMES_SESSION) == {1: another_telegram_user.username}
    update.message.reply_text.assert_called_once()


@pytest.mark.django_db
@pytest.mark.integration
def test_accept(
    update: Update,
    context: CallbackContext,
    telegram_user_with_phone: TelegramUser,
    another_telegram_user: TelegramUser,
) -> None:
    update.message.text = "1"
    context.user_data[_USERNAMES_SESSION] = {int(update.message.text): another_telegram_user}
    request = FriendRequest.objects.create(source=another_telegram_user, destination=telegram_user_with_phone)

    next_state = handle_accept(update, context)

    assert_conversation_end(next_state, context)
    assert not FriendRequest.objects.filter(pk=request.pk).exists()
    assert telegram_user_with_phone.friends.filter(id=another_telegram_user.id).exists()
    assert another_telegram_user.friends.filter(id=telegram_user_with_phone.id).exists()
    update.message.reply_text.assert_called_once_with(get_notification(another_telegram_user))
    context.bot.send_message.assert_called_once_with(
        chat_id=another_telegram_user.id, text=get_notification(telegram_user_with_phone)
    )


@pytest.mark.django_db
@pytest.mark.integration
def test_accept__stupid_choice(
    update: Update,
    context: CallbackContext,
    telegram_user_with_phone: TelegramUser,
    another_telegram_user: TelegramUser,
) -> None:
    update.message.text = "-1"
    context.user_data[_USERNAMES_SESSION] = {1: another_telegram_user}
    request = FriendRequest.objects.create(source=another_telegram_user, destination=telegram_user_with_phone)

    next_state = handle_accept(update, context)

    assert next_state == FriendStates.INPUT
    assert FriendRequest.objects.filter(pk=request.pk).exists()
    assert not telegram_user_with_phone.friends.filter(id=another_telegram_user.id).exists()
    assert not another_telegram_user.friends.filter(id=telegram_user_with_phone.id).exists()
    update.message.reply_text.assert_called_once_with(_STUPID_CHOICE)


@pytest.mark.django_db
@pytest.mark.integration
def test_accept__friend_canceled(
    update: Update,
    context: CallbackContext,
    telegram_user_with_phone: TelegramUser,
    another_telegram_user: TelegramUser,
) -> None:
    update.message.text = "1"
    context.user_data[_USERNAMES_SESSION] = {int(update.message.text): another_telegram_user}

    next_state = handle_accept(update, context)

    assert_conversation_end(next_state, context)
    assert not telegram_user_with_phone.friends.filter(id=another_telegram_user.id).exists()
    assert not another_telegram_user.friends.filter(id=telegram_user_with_phone.id).exists()
    update.message.reply_text.assert_called_once_with(_FRIEND_CANCEL)
    context.bot.send_message.assert_not_called()
