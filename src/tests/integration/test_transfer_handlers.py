from decimal import Decimal
from typing import List
from unittest.mock import MagicMock

import pytest
from telegram.ext import ConversationHandler

from app.internal.models.bank import BankAccount
from app.internal.models.user import TelegramUser
from app.internal.services.bank.transfer import parse_accrual
from app.internal.transport.bot.modules.transfer import (
    TransferStates,
    handle_transfer_accrual,
    handle_transfer_destination,
    handle_transfer_destination_document,
    handle_transfer_source_document,
    handle_transfer_start,
)
from app.internal.transport.bot.modules.transfer.handlers import (
    _ACCRUAL_GREATER_BALANCE_ERROR,
    _ACCRUAL_PARSE_ERROR,
    _ACCRUAL_SESSION,
    _BALANCE_ZERO_ERROR,
    _CHOSEN_FRIEND_SESSION,
    _DESTINATION_DOCUMENTS_SESSION,
    _DESTINATION_SESSION,
    _FRIEND_DOCUMENT_LIST_EMPTY_ERROR,
    _FRIEND_LIST_EMPTY_ERROR,
    _FRIEND_VARIANTS_SESSION,
    _SOURCE_DOCUMENT_LIST_EMPTY_ERROR,
    _SOURCE_DOCUMENTS_SESSION,
    _SOURCE_SESSION,
    _STUPID_CHOICE_ERROR,
    _TRANSFER_FAIL,
    _TRANSFER_SUCCESS,
    handle_transfer,
)
from tests.conftest import BALANCE


@pytest.mark.django_db
@pytest.mark.integration
def test_start(
    update: MagicMock,
    context: MagicMock,
    telegram_user_with_phone: TelegramUser,
    friend: TelegramUser,
    bank_accounts: List[BankAccount],
) -> None:
    next_state = handle_transfer_start(update, context)

    assert next_state == TransferStates.DESTINATION
    assert _SOURCE_DOCUMENTS_SESSION in context.user_data
    assert _FRIEND_VARIANTS_SESSION in context.user_data
    assert list(context.user_data[_SOURCE_DOCUMENTS_SESSION].values()) == bank_accounts
    assert list(context.user_data[_FRIEND_VARIANTS_SESSION].values()) == [friend]


@pytest.mark.django_db
@pytest.mark.integration
def test_start_friends_zero(
    update: MagicMock,
    context: MagicMock,
    telegram_user_with_phone: TelegramUser,
    bank_accounts: List[BankAccount],
) -> None:
    next_state = handle_transfer_start(update, context)

    assert next_state == ConversationHandler.END
    update.message.reply_text.assert_called_once_with(_FRIEND_LIST_EMPTY_ERROR)
    assert _SOURCE_DOCUMENTS_SESSION not in context.user_data
    assert _FRIEND_VARIANTS_SESSION not in context.user_data


@pytest.mark.django_db
@pytest.mark.integration
def test_start_source_documents_zero(
    update: MagicMock, context: MagicMock, telegram_user_with_phone: TelegramUser, friend: TelegramUser
) -> None:
    next_state = handle_transfer_start(update, context)

    assert next_state == ConversationHandler.END
    update.message.reply_text.assert_called_once_with(_SOURCE_DOCUMENT_LIST_EMPTY_ERROR)
    assert _SOURCE_DOCUMENTS_SESSION not in context.user_data


@pytest.mark.django_db
@pytest.mark.integration
def test_destination(
    update: MagicMock,
    context: MagicMock,
    telegram_user: TelegramUser,
    friend_with_account: TelegramUser,
    friend_account: BankAccount,
) -> None:
    context.user_data[_FRIEND_VARIANTS_SESSION] = {1: friend_with_account}
    update.message.text = "1"

    next_state = handle_transfer_destination(update, context)

    assert next_state == TransferStates.DESTINATION_DOCUMENT
    assert _CHOSEN_FRIEND_SESSION in context.user_data
    assert _DESTINATION_DOCUMENTS_SESSION in context.user_data
    assert context.user_data[_CHOSEN_FRIEND_SESSION] == friend_with_account
    assert list(context.user_data[_DESTINATION_DOCUMENTS_SESSION].values()) == [friend_account]


@pytest.mark.django_db
@pytest.mark.integration
def test_destination_stupid_choice(update: MagicMock, context: MagicMock, telegram_user: TelegramUser) -> None:
    context.user_data[_FRIEND_VARIANTS_SESSION] = {}
    update.message.text = "1"
    next_state = handle_transfer_destination(update, context)

    assert next_state == TransferStates.DESTINATION
    update.message.reply_text.assert_called_once_with(_STUPID_CHOICE_ERROR)
    assert _CHOSEN_FRIEND_SESSION not in context.user_data
    assert _DESTINATION_DOCUMENTS_SESSION not in context.user_data


@pytest.mark.django_db
@pytest.mark.integration
def test_destination_friend_document_list_empty(
    update: MagicMock, context: MagicMock, telegram_user: TelegramUser, friend: TelegramUser
) -> None:
    context.user_data[_FRIEND_VARIANTS_SESSION] = {1: friend}
    update.message.text = "1"

    next_state = handle_transfer_destination(update, context)

    assert next_state == TransferStates.DESTINATION
    update.message.reply_text.assert_called_once_with(_FRIEND_DOCUMENT_LIST_EMPTY_ERROR)
    assert _CHOSEN_FRIEND_SESSION in context.user_data
    assert context.user_data[_CHOSEN_FRIEND_SESSION] == friend
    assert _DESTINATION_DOCUMENTS_SESSION not in context.user_data


@pytest.mark.django_db
@pytest.mark.integration
def test_destination_document(
    update: MagicMock, context: MagicMock, bank_account: BankAccount, friend_account: BankAccount
) -> None:
    update.message.text = "1"
    context.user_data[_DESTINATION_DOCUMENTS_SESSION] = {1: friend_account}
    context.user_data[_SOURCE_DOCUMENTS_SESSION] = {1: bank_account}

    next_state = handle_transfer_destination_document(update, context)

    assert next_state == TransferStates.SOURCE_DOCUMENT
    assert _DESTINATION_SESSION in context.user_data
    assert context.user_data[_DESTINATION_SESSION] == friend_account


@pytest.mark.django_db
@pytest.mark.integration
def test_destination_document_stupid_choice(update: MagicMock, context: MagicMock, friend_account: BankAccount) -> None:
    update.message.text = "-1"
    context.user_data[_DESTINATION_DOCUMENTS_SESSION] = {1: friend_account}

    next_state = handle_transfer_destination_document(update, context)

    assert next_state == TransferStates.DESTINATION_DOCUMENT
    update.message.reply_text.assert_called_once_with(_STUPID_CHOICE_ERROR)
    assert _DESTINATION_SESSION not in context.user_data


@pytest.mark.django_db
@pytest.mark.integration
def test_source_document(update: MagicMock, context: MagicMock, bank_account: BankAccount) -> None:
    update.message.text = "1"
    context.user_data[_SOURCE_DOCUMENTS_SESSION] = {1: bank_account}

    next_state = handle_transfer_source_document(update, context)

    assert next_state == TransferStates.ACCRUAL
    assert _SOURCE_SESSION in context.user_data
    assert context.user_data[_SOURCE_SESSION] == bank_account


@pytest.mark.django_db
@pytest.mark.integration
def test_source_document_stupid_choice(update: MagicMock, context: MagicMock, bank_account: BankAccount) -> None:
    update.message.text = "-1"
    context.user_data[_SOURCE_DOCUMENTS_SESSION] = {1: bank_account}

    next_state = handle_transfer_source_document(update, context)

    assert next_state == TransferStates.SOURCE_DOCUMENT
    update.message.reply_text.assert_called_once_with(_STUPID_CHOICE_ERROR)
    assert _SOURCE_SESSION not in context.user_data


@pytest.mark.django_db
@pytest.mark.integration
def test_source_document_balance_zero(update: MagicMock, context: MagicMock, bank_account: BankAccount) -> None:
    update.message.text = "1"
    context.user_data[_SOURCE_DOCUMENTS_SESSION] = {1: bank_account}
    bank_account.balance = 0
    bank_account.save()

    next_state = handle_transfer_source_document(update, context)

    assert next_state == TransferStates.SOURCE_DOCUMENT
    update.message.reply_text.assert_called_once_with(_BALANCE_ZERO_ERROR)
    assert _SOURCE_SESSION not in context.user_data


@pytest.mark.django_db
@pytest.mark.integration
def test_accrual(update: MagicMock, context: MagicMock, bank_account: BankAccount, friend_account: BankAccount) -> None:
    update.message.text = str(bank_account.balance)
    accrual = parse_accrual(update.message.text)
    context.user_data[_SOURCE_SESSION] = bank_account
    context.user_data[_DESTINATION_SESSION] = friend_account

    next_state = handle_transfer_accrual(update, context)

    assert next_state == TransferStates.CONFIRM
    assert _ACCRUAL_SESSION in context.user_data
    assert context.user_data[_ACCRUAL_SESSION] == accrual


@pytest.mark.django_db
@pytest.mark.integration
def test_accrual_parse_error(
    update: MagicMock, context: MagicMock, bank_account: BankAccount, friend_account: BankAccount
) -> None:
    update.message.text = "0"

    next_state = handle_transfer_accrual(update, context)

    assert next_state == TransferStates.ACCRUAL
    update.message.reply_text.assert_called_once_with(_ACCRUAL_PARSE_ERROR)
    assert _ACCRUAL_SESSION not in context.user_data


@pytest.mark.django_db
@pytest.mark.integration
def test_accrual_extract_error(
    update: MagicMock, context: MagicMock, bank_account: BankAccount, friend_account: BankAccount
) -> None:
    update.message.text = str(bank_account.balance * 2)
    context.user_data[_SOURCE_SESSION] = bank_account

    next_state = handle_transfer_accrual(update, context)

    assert next_state == TransferStates.ACCRUAL
    update.message.reply_text.assert_called_once_with(_ACCRUAL_GREATER_BALANCE_ERROR)
    assert _ACCRUAL_SESSION not in context.user_data


@pytest.mark.django_db
@pytest.mark.integration
def test_transfer(
    update: MagicMock, context: MagicMock, bank_account: BankAccount, another_account: BankAccount
) -> None:
    _assert_transfer(update, context, bank_account, another_account, BALANCE, True)


@pytest.mark.django_db
@pytest.mark.integration
def test_transfer_fail(
    update: MagicMock, context: MagicMock, bank_account: BankAccount, another_account: BankAccount
) -> None:
    _assert_transfer(update, context, bank_account, another_account, BALANCE * 2, False)


def _assert_transfer(
    update: MagicMock,
    context: MagicMock,
    source: BankAccount,
    destination: BankAccount,
    accrual: Decimal,
    is_success: bool,
) -> None:
    context.user_data[_SOURCE_SESSION] = source
    context.user_data[_DESTINATION_SESSION] = destination
    context.user_data[_ACCRUAL_SESSION] = accrual
    context.user_data[_SOURCE_DOCUMENTS_SESSION] = None
    context.user_data[_DESTINATION_DOCUMENTS_SESSION] = None
    context.user_data[_CHOSEN_FRIEND_SESSION] = None
    context.user_data[_FRIEND_VARIANTS_SESSION] = None

    next_state = handle_transfer(update, context)

    assert next_state == ConversationHandler.END
    update.message.reply_text.assert_called_once_with(_TRANSFER_SUCCESS if is_success else _TRANSFER_FAIL)
    assert len(context.user_data) == 0
