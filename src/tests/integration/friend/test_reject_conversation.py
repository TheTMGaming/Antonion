from unittest.mock import MagicMock

import pytest
from telegram.ext import ConversationHandler

from app.internal.models.user import FriendRequest, TelegramUser
from app.internal.transport.bot.modules.friends.FriendStates import FriendStates
from app.internal.transport.bot.modules.friends.reject_conversation import (
    _REJECT_SUCCESS,
    _STUPID_CHOICE,
    _USERNAMES_SESSION,
    get_notification,
    handle_reject,
)


@pytest.mark.django_db
@pytest.mark.integration
def test_reject(
    update: MagicMock, context: MagicMock, telegram_user_with_phone: TelegramUser, another_telegram_user: TelegramUser
) -> None:
    update.message.text = "1"
    context.user_data[_USERNAMES_SESSION] = {int(update.message.text): another_telegram_user}
    request = FriendRequest.objects.create(source=another_telegram_user, destination=telegram_user_with_phone)

    next_state = handle_reject(update, context)

    assert next_state == ConversationHandler.END
    assert not FriendRequest.objects.filter(pk=request.pk).exists()
    update.message.reply_text.assert_called_once_with(_REJECT_SUCCESS)
    context.bot.send_message.assert_called_once_with(
        chat_id=another_telegram_user.id, text=get_notification(telegram_user_with_phone)
    )
    assert len(context.user_data) == 0


@pytest.mark.django_db
@pytest.mark.integration
def test_reject__error(
    update: MagicMock, context: MagicMock, telegram_user_with_phone: TelegramUser, another_telegram_user: TelegramUser
) -> None:
    update.message.text = "-1"
    context.user_data[_USERNAMES_SESSION] = {1: another_telegram_user}

    next_state = handle_reject(update, context)

    assert next_state == FriendStates.INPUT
    update.message.reply_text.assert_called_once_with(_STUPID_CHOICE)
    assert len(context.user_data) == 0
