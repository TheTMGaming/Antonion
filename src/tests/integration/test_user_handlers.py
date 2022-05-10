from unittest.mock import MagicMock

import pytest
from telegram import User
from telegram.ext import ConversationHandler

from app.internal.models.bank import BankAccount, Transaction
from app.internal.models.user import TelegramUser
from app.internal.transport.bot.modules.user.handlers import (
    _RELATION_LIST_EMPTY,
    _UPDATING_DETAILS,
    _WELCOME as welcome_user,
    handle_me,
    handle_relations,
    handle_start,
)
from app.internal.transport.bot.modules.user.phone_conversation import (
    _INVALID_PHONE,
    _UPDATING_PHONE,
    _WELCOME,
    handle_phone,
    handle_phone_start,
)
from app.internal.transport.bot.modules.user.PhoneStates import PhoneStates
from tests.integration.general import assert_conversation_end, assert_conversation_start


@pytest.mark.django_db
@pytest.mark.integration
def test_start__adding(update: MagicMock, user: User) -> None:
    handle_start(update, None)

    assert TelegramUser.objects.filter(
        id=user.id, first_name=user.first_name, last_name=user.last_name, username=user.username
    ).exists()
    update.message.reply_text.assert_called_once_with(welcome_user.format(username=user.username))


@pytest.mark.django_db
@pytest.mark.integration
def test_start__updating(update: MagicMock, telegram_user: TelegramUser, user: User) -> None:
    user.username = user.username[::-1]
    user.first_name = user.first_name[::-1]
    user.last_name = user.last_name[::-1]

    update.effective_user = user

    handle_start(update, None)

    assert TelegramUser.objects.filter(
        id=telegram_user.id, first_name=user.first_name, last_name=user.last_name, username=user.username
    ).exists()
    update.message.reply_text.assert_called_once_with(_UPDATING_DETAILS)


@pytest.mark.django_db
@pytest.mark.integration
def test_me(update: MagicMock, context: MagicMock, telegram_user_with_phone: TelegramUser) -> None:
    handle_me(update, context)
    update.message.reply_text.assert_called_once()


@pytest.mark.django_db
@pytest.mark.integration
def test_phone_start(update: MagicMock, context: MagicMock, telegram_user_with_phone: TelegramUser) -> None:
    next_state = handle_phone_start(update, context)

    assert next_state == PhoneStates.INPUT
    assert_conversation_start(context)
    update.message.reply_text.assert_called_once_with(_WELCOME)


@pytest.mark.django_db
@pytest.mark.integration
@pytest.mark.parametrize(
    ["text", "is_set"],
    [
        ["88005553535", True],
        ["8-800-555-35-35", True],
        ["8.800.555.35.35", True],
        ["8(800)-555-35-35", True],
        ["8 (800)-555-35-35", True],
        ["8(800) 555 35 35", True],
        ["8 (800) 555 35 35", True],
        ["88005553535         ", True],
        ["8 800 555 35 35", True],
        ["88005553535 a b", True],
        ["                ", False],
        ["aaaaaaaaaaa", False],
        ["8800", False],
        ["88005553535 1 2", False],
        ["a b 88005553535", False],
        ["        88005553535", False],
        ["aaa        88005553535", False],
        ["    88005553535", False],
    ],
)
def test_phone(update: MagicMock, context: MagicMock, telegram_user: TelegramUser, text: str, is_set: bool) -> None:
    update.message.text = text

    next_state = handle_phone(update, context)

    actual = TelegramUser.objects.get(pk=telegram_user.pk)

    assert bool(actual.phone) == is_set
    update.message.reply_text.assert_called_once_with(_UPDATING_PHONE if is_set else _INVALID_PHONE)
    if is_set:
        assert_conversation_end(next_state, context)
    else:
        assert next_state == PhoneStates.INPUT


@pytest.mark.django_db
@pytest.mark.integration
def test_getting_relations(
    update: MagicMock,
    context: MagicMock,
    telegram_user_with_phone: TelegramUser,
    bank_account: BankAccount,
    another_account: BankAccount,
) -> None:
    Transaction.objects.create(source=bank_account, destination=another_account)

    handle_relations(update, context)

    update.message.reply_text.assert_called_once()


@pytest.mark.django_db
@pytest.mark.integration
def test_getting_relations__list_is_empty(
    update: MagicMock, context: MagicMock, telegram_user_with_phone: TelegramUser
) -> None:
    handle_relations(update, context)

    update.message.reply_text.assert_called_once_with(_RELATION_LIST_EMPTY)
