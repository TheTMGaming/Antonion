from typing import List
from unittest.mock import MagicMock

import pytest
from telegram.ext import ConversationHandler

from app.internal.models.bank import BankAccount, BankCard
from app.internal.models.user import TelegramUser
from app.internal.transport.bot.modules.balance import BalanceStates, handle_balance_start
from app.internal.transport.bot.modules.balance.handlers import (
    _DOCUMENTS_SESSION,
    _LIST_EMPTY_MESSAGE,
    _STUPID_CHOICE,
    handle_balance_choice,
)


@pytest.mark.django_db
@pytest.mark.integration
def test_balance_start(
    update: MagicMock,
    context: MagicMock,
    telegram_user_with_phone: TelegramUser,
    bank_accounts: List[BankAccount],
    cards: List[BankCard],
) -> None:
    handle_balance_start(update, context)

    assert _DOCUMENTS_SESSION in context.user_data
    assert list(context.user_data[_DOCUMENTS_SESSION].values()) == [*bank_accounts, *cards]


@pytest.mark.django_db
@pytest.mark.integration
def test_balance_start_documents_zero(
    update: MagicMock, context: MagicMock, telegram_user_with_phone: TelegramUser
) -> None:
    handle_balance_start(update, context)

    assert _DOCUMENTS_SESSION not in context.user_data
    update.message.reply_text.assert_called_once_with(_LIST_EMPTY_MESSAGE)


@pytest.mark.django_db
@pytest.mark.integration
def test_balance_choice(update: MagicMock, context: MagicMock, bank_account: BankAccount) -> None:
    update.message.text = "1"
    context.user_data[_DOCUMENTS_SESSION] = {1: bank_account}

    next_state = handle_balance_choice(update, context)

    assert next_state == ConversationHandler.END


@pytest.mark.django_db
@pytest.mark.integration
def test_balance_stupid_choice(update: MagicMock, context: MagicMock, bank_account: BankAccount) -> None:
    update.message.text = "-1"
    context.user_data[_DOCUMENTS_SESSION] = {1: bank_account}

    next_state = handle_balance_choice(update, context)

    assert next_state == BalanceStates.CHOICE
    update.message.reply_text.assert_called_once_with(_STUPID_CHOICE)
