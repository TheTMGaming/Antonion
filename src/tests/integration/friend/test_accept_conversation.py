from unittest.mock import MagicMock

import pytest
from telegram.ext import ConversationHandler

from app.internal.models.user import FriendRequest, TelegramUser
from app.internal.transport.bot.modules.friends.accept_conversation import (
    _FRIEND_CANCEL,
    _STUPID_CHOICE,
    _USERNAMES_SESSION,
    get_notification,
    handle_accept,
)
from app.internal.transport.bot.modules.friends.FriendStates import FriendStates


@pytest.mark.django_db
@pytest.mark.integration
def test_accept(
    update: MagicMock, context: MagicMock, telegram_user_with_phone: TelegramUser, another_telegram_user: TelegramUser
) -> None:
    update.message.text = "1"
    context.user_data[_USERNAMES_SESSION] = {int(update.message.text): another_telegram_user}
    request = FriendRequest.objects.create(source=another_telegram_user, destination=telegram_user_with_phone)

    next_state = handle_accept(update, context)

    assert next_state == ConversationHandler.END
    assert not FriendRequest.objects.filter(pk=request.pk).exists()
    assert telegram_user_with_phone.friends.filter(id=another_telegram_user.id).exists()
    assert another_telegram_user.friends.filter(id=telegram_user_with_phone.id).exists()
    update.message.reply_text.assert_called_once_with(get_notification(another_telegram_user))
    context.bot.send_message.assert_called_once_with(
        chat_id=another_telegram_user.id, text=get_notification(telegram_user_with_phone)
    )
    assert len(context.user_data) == 0


@pytest.mark.django_db
@pytest.mark.integration
def test_accept__stupid_choice(
    update: MagicMock, context: MagicMock, telegram_user_with_phone: TelegramUser, another_telegram_user: TelegramUser
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
    assert len(context.user_data) == 0


@pytest.mark.django_db
@pytest.mark.integration
def test_accept__friend_canceled(
    update: MagicMock, context: MagicMock, telegram_user_with_phone: TelegramUser, another_telegram_user: TelegramUser
) -> None:
    update.message.text = "1"
    context.user_data[_USERNAMES_SESSION] = {int(update.message.text): another_telegram_user}

    next_state = handle_accept(update, context)

    assert next_state == ConversationHandler.END
    assert not telegram_user_with_phone.friends.filter(id=another_telegram_user.id).exists()
    assert not another_telegram_user.friends.filter(id=telegram_user_with_phone.id).exists()
    update.message.reply_text.assert_called_once_with(_FRIEND_CANCEL)
    assert len(context.user_data) == 0
