from decimal import Decimal
from typing import List
from unittest.mock import MagicMock

import pytest

from app.internal.bot import (
    _ACCRUAL_GREATER_BALANCE_ERROR,
    _ACCRUAL_PARSE_ERROR,
    _ACCRUAL_SESSION,
    _ACCRUAL_WELCOME,
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
    handle_getting_accrual,
    handle_getting_destination,
    handle_getting_destination_document,
    handle_getting_source_document,
    handle_start,
    handle_transfer,
)
from app.internal.bot.modules.transfer.TransferStates import TransferStates
from app.internal.models.bank import BankAccount, BankCard, BankObject
from app.internal.models.user import TelegramUser
from app.internal.services.bank.transfer import parse_accrual
from tests.conftest import BALANCE
from tests.integration.general import assert_conversation_end, assert_conversation_start


@pytest.mark.django_db
@pytest.mark.integration
def test_start(
    update: MagicMock,
    context: MagicMock,
    telegram_user_with_phone,
    friends: List[TelegramUser],
    bank_accounts: List[BankAccount],
) -> None:
    next_state = handle_start(update, context)

    assert_conversation_start(context)
    assert next_state == TransferStates.DESTINATION
    assert _SOURCE_DOCUMENTS_SESSION in context.user_data
    assert _FRIEND_VARIANTS_SESSION in context.user_data
    assert type(context.user_data[_SOURCE_DOCUMENTS_SESSION]) is dict
    assert type(context.user_data[_FRIEND_VARIANTS_SESSION]) is dict
    assert sorted(context.user_data[_SOURCE_DOCUMENTS_SESSION].values(), key=str) == sorted(bank_accounts, key=str)
    assert sorted(context.user_data[_FRIEND_VARIANTS_SESSION].values(), key=str) == sorted(friends, key=str)
    update.message.reply_text.assert_called_once()


@pytest.mark.django_db
@pytest.mark.integration
def test_start__friends_list_is_empty(
    update: MagicMock,
    context: MagicMock,
    telegram_user_with_phone,
    bank_accounts: List[BankAccount],
) -> None:
    next_state = handle_start(update, context)

    assert_conversation_end(next_state, context)
    update.message.reply_text.assert_called_once_with(_FRIEND_LIST_EMPTY_ERROR)


@pytest.mark.django_db
@pytest.mark.integration
def test_start__source_documents_list_is_empty(
    update: MagicMock, context: MagicMock, telegram_user_with_phone, friend: TelegramUser
) -> None:
    next_state = handle_start(update, context)

    assert_conversation_end(next_state, context)
    update.message.reply_text.assert_called_once_with(_SOURCE_DOCUMENT_LIST_EMPTY_ERROR)


@pytest.mark.django_db
@pytest.mark.integration
def test_getting_destination(
    update: MagicMock,
    context: MagicMock,
    telegram_user: TelegramUser,
    friend_with_account: TelegramUser,
    friend_account: BankAccount,
) -> None:
    context.user_data[_FRIEND_VARIANTS_SESSION] = {1: friend_with_account}
    update.message.text = "1"

    next_state = handle_getting_destination(update, context)

    assert next_state == TransferStates.DESTINATION_DOCUMENT
    assert _CHOSEN_FRIEND_SESSION in context.user_data
    assert _DESTINATION_DOCUMENTS_SESSION in context.user_data
    assert context.user_data[_CHOSEN_FRIEND_SESSION] == friend_with_account
    assert type(context.user_data[_DESTINATION_DOCUMENTS_SESSION]) is dict
    assert list(context.user_data[_DESTINATION_DOCUMENTS_SESSION].values()) == [friend_account]
    update.message.reply_text.assert_called_once()


@pytest.mark.django_db
@pytest.mark.integration
def test_getting_destination__stupid_choice(update: MagicMock, context: MagicMock, telegram_user: TelegramUser) -> None:
    context.user_data[_FRIEND_VARIANTS_SESSION] = {}
    update.message.text = "1"
    next_state = handle_getting_destination(update, context)

    assert next_state == TransferStates.DESTINATION
    update.message.reply_text.assert_called_once_with(_STUPID_CHOICE_ERROR)
    assert _CHOSEN_FRIEND_SESSION not in context.user_data
    assert _DESTINATION_DOCUMENTS_SESSION not in context.user_data


@pytest.mark.django_db
@pytest.mark.integration
def test_getting_destination__friend_documents_list_is_empty(
    update: MagicMock, context: MagicMock, telegram_user: TelegramUser, friend: TelegramUser
) -> None:
    context.user_data[_FRIEND_VARIANTS_SESSION] = {1: friend}
    update.message.text = "1"

    next_state = handle_getting_destination(update, context)

    assert next_state == TransferStates.DESTINATION
    update.message.reply_text.assert_called_once_with(_FRIEND_DOCUMENT_LIST_EMPTY_ERROR)
    assert _CHOSEN_FRIEND_SESSION in context.user_data
    assert context.user_data[_CHOSEN_FRIEND_SESSION] == friend
    assert _DESTINATION_DOCUMENTS_SESSION not in context.user_data


@pytest.mark.django_db
@pytest.mark.integration
def test_getting_destination_document__bank_account(
    update: MagicMock, context: MagicMock, bank_account: BankAccount, friend_account: BankAccount
) -> None:
    _test_getting_destination_document__bank_object(update, context, bank_account, friend_account)


@pytest.mark.django_db
@pytest.mark.integration
def test_getting_destination_document__card(
    update: MagicMock, context: MagicMock, bank_account: BankAccount, friend_card: BankCard
) -> None:
    _test_getting_destination_document__bank_object(update, context, bank_account, friend_card)


def _test_getting_destination_document__bank_object(
    update: MagicMock, context: MagicMock, bank_account: BankAccount, obj: BankObject
) -> None:
    update.message.text = "1"
    context.user_data[_SOURCE_DOCUMENTS_SESSION] = {1: bank_account}
    context.user_data[_DESTINATION_DOCUMENTS_SESSION] = {1: obj}

    next_state = handle_getting_destination_document(update, context)

    assert next_state == TransferStates.SOURCE_DOCUMENT
    assert _DESTINATION_SESSION in context.user_data
    assert type(context.user_data[_DESTINATION_SESSION]) is BankAccount
    assert context.user_data[_DESTINATION_SESSION] == (obj if isinstance(obj, BankAccount) else obj.bank_account)
    update.message.reply_text.assert_called_once()


@pytest.mark.django_db
@pytest.mark.integration
def test_getting_destination_document__stupid_choice(
    update: MagicMock, context: MagicMock, friend_account: BankAccount
) -> None:
    update.message.text = "-1"
    context.user_data[_DESTINATION_DOCUMENTS_SESSION] = {1: friend_account}

    next_state = handle_getting_destination_document(update, context)

    assert next_state == TransferStates.DESTINATION_DOCUMENT
    update.message.reply_text.assert_called_once_with(_STUPID_CHOICE_ERROR)
    assert _DESTINATION_SESSION not in context.user_data


@pytest.mark.django_db
@pytest.mark.integration
def test_getting_source_document__bank_account(
    update: MagicMock, context: MagicMock, bank_account: BankAccount
) -> None:
    _test_getting_source_document__bank_object(update, context, bank_account)


@pytest.mark.django_db
@pytest.mark.integration
def test_getting_source_document__card(update: MagicMock, context: MagicMock, card: BankCard) -> None:
    _test_getting_source_document__bank_object(update, context, card)


def _test_getting_source_document__bank_object(update: MagicMock, context: MagicMock, obj: BankObject) -> None:
    update.message.text = "1"
    context.user_data[_SOURCE_DOCUMENTS_SESSION] = {1: obj}

    next_state = handle_getting_source_document(update, context)

    assert next_state == TransferStates.ACCRUAL
    assert _SOURCE_SESSION in context.user_data
    assert context.user_data[_SOURCE_SESSION] == (obj if isinstance(obj, BankAccount) else obj.bank_account)
    update.message.reply_text.assert_called_once_with(_ACCRUAL_WELCOME)


@pytest.mark.django_db
@pytest.mark.integration
def test_getting_source_document__stupid_choice(
    update: MagicMock, context: MagicMock, bank_account: BankAccount
) -> None:
    update.message.text = "-1"
    context.user_data[_SOURCE_DOCUMENTS_SESSION] = {1: bank_account}

    next_state = handle_getting_source_document(update, context)

    assert next_state == TransferStates.SOURCE_DOCUMENT
    update.message.reply_text.assert_called_once_with(_STUPID_CHOICE_ERROR)
    assert _SOURCE_SESSION not in context.user_data


@pytest.mark.django_db
@pytest.mark.integration
def test_getting_source_document__balance_is_zero(
    update: MagicMock, context: MagicMock, bank_account: BankAccount
) -> None:
    update.message.text = "1"
    context.user_data[_SOURCE_DOCUMENTS_SESSION] = {1: bank_account}
    bank_account.balance = 0
    bank_account.save()

    next_state = handle_getting_source_document(update, context)

    assert next_state == TransferStates.SOURCE_DOCUMENT
    update.message.reply_text.assert_called_once_with(_BALANCE_ZERO_ERROR)
    assert _SOURCE_SESSION not in context.user_data


@pytest.mark.django_db
@pytest.mark.integration
def test_getting_accrual(
    update: MagicMock, context: MagicMock, bank_account: BankAccount, friend_account: BankAccount
) -> None:
    update.message.text = str(bank_account.balance)
    accrual = parse_accrual(update.message.text)
    context.user_data[_SOURCE_SESSION] = bank_account
    context.user_data[_DESTINATION_SESSION] = friend_account

    next_state = handle_getting_accrual(update, context)

    assert next_state == TransferStates.CONFIRM
    assert _ACCRUAL_SESSION in context.user_data
    assert context.user_data[_ACCRUAL_SESSION] == accrual
    update.message.reply_text.assert_called_once()


@pytest.mark.django_db
@pytest.mark.integration
def test_getting_accrual__parse_error(
    update: MagicMock, context: MagicMock, bank_account: BankAccount, friend_account: BankAccount
) -> None:
    update.message.text = "0"

    next_state = handle_getting_accrual(update, context)

    assert next_state == TransferStates.ACCRUAL
    update.message.reply_text.assert_called_once_with(_ACCRUAL_PARSE_ERROR)
    assert _ACCRUAL_SESSION not in context.user_data


@pytest.mark.django_db
@pytest.mark.integration
def test_getting_accrual__extracting_error(
    update: MagicMock, context: MagicMock, bank_account: BankAccount, friend_account: BankAccount
) -> None:
    update.message.text = str(bank_account.balance * 2)
    context.user_data[_SOURCE_SESSION] = bank_account

    next_state = handle_getting_accrual(update, context)

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

    assert_conversation_end(next_state, context)
    update.message.reply_text.assert_called_once_with(_TRANSFER_SUCCESS if is_success else _TRANSFER_FAIL)
    context.bot.send_message.assert_called_once() if is_success else context.bot.send_message.assert_not_called()
