from unittest.mock import MagicMock

import pytest

from app.internal.bot.modules.friends.FriendStates import FriendStates
from app.internal.bot.modules.friends.reject_conversation import (
    _REJECT_SUCCESS,
    _STUPID_CHOICE,
    _USERNAMES_SESSION,
    get_notification,
    handle_reject,
    handle_reject_start,
)
from app.internal.user.db.models import FriendRequest, TelegramUser
from tests.integration.general import assert_conversation_end, assert_conversation_start


@pytest.mark.django_db
@pytest.mark.integration
def test_reject_start(
    update: MagicMock, context: MagicMock, telegram_user_with_phone, another_telegram_user: TelegramUser
) -> None:
    FriendRequest.objects.create(source=another_telegram_user, destination=telegram_user_with_phone)

    next_state = handle_reject_start(update, context)

    assert next_state == FriendStates.INPUT
    assert_conversation_start(context)
    assert _USERNAMES_SESSION in context.user_data
    assert context.user_data[_USERNAMES_SESSION] == {1: another_telegram_user.username}
    update.message.reply_text.assert_called_once()


@pytest.mark.django_db
@pytest.mark.integration
def test_reject(
    update: MagicMock, context: MagicMock, telegram_user_with_phone, another_telegram_user: TelegramUser
) -> None:
    update.message.text = "1"
    context.user_data[_USERNAMES_SESSION] = {int(update.message.text): another_telegram_user}
    request = FriendRequest.objects.create(source=another_telegram_user, destination=telegram_user_with_phone)

    next_state = handle_reject(update, context)

    assert_conversation_end(next_state, context)
    assert not FriendRequest.objects.filter(pk=request.pk).exists()
    update.message.reply_text.assert_called_once_with(_REJECT_SUCCESS)
    context.bot.send_message.assert_called_once_with(
        chat_id=another_telegram_user.id, text=get_notification(telegram_user_with_phone)
    )


@pytest.mark.django_db
@pytest.mark.integration
def test_reject__stupid_choice(
    update: MagicMock, context: MagicMock, telegram_user_with_phone, another_telegram_user: TelegramUser
) -> None:
    update.message.text = "-1"
    context.user_data[_USERNAMES_SESSION] = {1: another_telegram_user}

    next_state = handle_reject(update, context)

    assert next_state == FriendStates.INPUT
    update.message.reply_text.assert_called_once_with(_STUPID_CHOICE)
