from decimal import Decimal
from enum import IntEnum, auto
from itertools import chain
from typing import List, Type

import pytest

from app.internal.models.bank import BankAccount, BankCard, BankObject, Transaction
from app.internal.services.bank.transfer import can_extract_from, is_balance_zero, parse_accrual, try_transfer
from tests.unit.bank.conftest import BALANCE


class TransferError(IntEnum):
    NONE = auto()
    OPERATION = auto()
    VALIDATION = auto()


@pytest.mark.django_db
@pytest.mark.unit
def test_checking_balance_zero(bank_account: BankAccount, cards: List[BankCard]) -> None:
    bank_account.balance = 0
    bank_account.save()

    card = BankCard.objects.filter(bank_account=bank_account).first()

    assert is_balance_zero(bank_account)
    assert is_balance_zero(card)


@pytest.mark.unit
@pytest.mark.parametrize(
    ["digits", "expected"],
    [
        ["0", None],
        ["-0", None],
        ["0.0", None],
        ["-1", None],
        ["-0.1", None],
        ["-0.01", None],
        ["-0.001", None],
        ["-0.001", None],
        ["-1", None],
        ["0.009", "0.01"],
        ["13", "13"],
        ["0.1", "0.1"],
        ["1.99", "1.99"],
        ["1.990", "1.99"],
        ["1.994", "1.99"],
        ["1.995", "2"],
        ["1.999999999999999", "2"],
        ["9.99", "9.99"],
        ["9.999", "10"],
        ["9" * BankAccount.DIGITS_COUNT, "9" * BankAccount.DIGITS_COUNT],
        ["-" + "9" * BankAccount.DIGITS_COUNT, None],
        ["9" * (BankAccount.DIGITS_COUNT + 1), None],
        ["-" + "9" * (BankAccount.DIGITS_COUNT + 1), None],
        [
            "9" * BankAccount.DIGITS_COUNT + "." + "9" * BankAccount.DECIMAL_PLACES,
            "9" * BankAccount.DIGITS_COUNT + "." + "9" * BankAccount.DECIMAL_PLACES,
        ],
        ["-" + "9" * BankAccount.DIGITS_COUNT + "." + "9" * BankAccount.DECIMAL_PLACES, None],
        ["9" * (BankAccount.DIGITS_COUNT + 1) + "." + "9" * BankAccount.DECIMAL_PLACES, None],
        ["-" + "9" * (BankAccount.DIGITS_COUNT + 1) + "." + "9" * BankAccount.DECIMAL_PLACES, None],
    ],
)
def test_parsing_accrual(digits: str, expected: str):
    if expected is None:
        with pytest.raises(ValueError):
            parse_accrual(digits)
    else:
        assert parse_accrual(digits) == Decimal(expected)


@pytest.mark.django_db
@pytest.mark.unit
@pytest.mark.parametrize(
    ["subtracted_value", "expected"],
    list(
        chain(
            *(
                [
                    [0, True],
                    [Decimal(f"{sign}0.1"), not bool(sign)],
                    [Decimal(f"{sign}0.01"), not bool(sign)],
                    [Decimal(f"{sign}0.9"), not bool(sign)],
                    [Decimal(f"{sign}0.99"), not bool(sign)],
                    [Decimal(f"{sign}0.09"), not bool(sign)],
                ]
                for sign in ["", "-"]
            )
        )
    ),
)
def test_checking_extract(bank_account: BankAccount, card: BankCard, subtracted_value: Decimal, expected: bool):
    accrual = Decimal(bank_account.balance - subtracted_value)

    assert can_extract_from(bank_account, accrual) == expected
    assert can_extract_from(card, accrual) == expected


TRANSFER_PARAMETERS = [
    ["accrual", "error_type"],
    [
        [Decimal("1"), TransferError.NONE],
        [Decimal("0.01"), TransferError.NONE],
        [Decimal("0.09"), TransferError.NONE],
        [Decimal("0.99"), TransferError.NONE],
        [BALANCE, TransferError.NONE],
        [BALANCE - Decimal("0.01"), TransferError.NONE],
        [BALANCE - Decimal("0.09"), TransferError.NONE],
        [BALANCE - Decimal("1"), TransferError.NONE],
        [BALANCE - Decimal("1.01"), TransferError.NONE],
        [BALANCE - Decimal("1.09"), TransferError.NONE],
        [BALANCE - Decimal("1.99"), TransferError.NONE],
        *([Decimal(i), TransferError.NONE] for i in range(1, int(BALANCE), int(BALANCE) // 4)),
        [BALANCE + Decimal("0.01"), TransferError.OPERATION],
        [BALANCE + Decimal("1"), TransferError.OPERATION],
        [BALANCE + Decimal("10"), TransferError.OPERATION],
        [BALANCE + Decimal("100"), TransferError.OPERATION],
        [BALANCE * 2, TransferError.OPERATION],
        [Decimal("0"), TransferError.VALIDATION],
        [Decimal("0.001"), TransferError.VALIDATION],
        [Decimal("-0"), TransferError.VALIDATION],
        [Decimal("-0.01"), TransferError.VALIDATION],
        [Decimal("-0.001"), TransferError.VALIDATION],
        [Decimal("-0.001"), TransferError.VALIDATION],
        [-BALANCE, TransferError.VALIDATION],
        [-BALANCE * 2, TransferError.VALIDATION],
    ],
]


@pytest.mark.django_db
@pytest.mark.unit
@pytest.mark.parametrize(*TRANSFER_PARAMETERS)
def test_transfer_account_to_account(
    bank_account: BankAccount, another_account: BankAccount, accrual: Decimal, error_type: TransferError
) -> None:
    _assert_documents_transfer(bank_account, another_account, accrual, error_type)


@pytest.mark.django_db
@pytest.mark.unit
@pytest.mark.parametrize(*TRANSFER_PARAMETERS)
def test_transfer_account_to_card(
    bank_account: BankAccount, another_card: BankCard, accrual: Decimal, error_type: TransferError
) -> None:
    _assert_documents_transfer(bank_account, another_card, accrual, error_type)


@pytest.mark.django_db
@pytest.mark.unit
@pytest.mark.parametrize(*TRANSFER_PARAMETERS)
def test_transfer_card_to_account(
    card: BankCard, another_account: BankAccount, accrual: Decimal, error_type: TransferError
) -> None:
    _assert_documents_transfer(card, another_account, accrual, error_type)


@pytest.mark.django_db
@pytest.mark.unit
@pytest.mark.parametrize(*TRANSFER_PARAMETERS)
def test_transfer_card_to_card(
    card: BankCard, another_card: BankCard, accrual: Decimal, error_type: TransferError
) -> None:
    _assert_documents_transfer(card, another_card, accrual, error_type)


def _assert_documents_transfer(
    source: BankObject, destination: BankObject, accrual: Decimal, error_type: TransferError
) -> None:
    if error_type == TransferError.VALIDATION:
        with pytest.raises(ValueError):
            try_transfer(source, destination, accrual)

        return

    is_error = error_type == TransferError.OPERATION

    source_start, destination_start = source.get_balance(), destination.get_balance()
    source_end, destination_end = (
        (source_start - accrual, destination_start + accrual) if not is_error else (source_start, destination_start)
    )

    is_transfer = try_transfer(source, destination, accrual)

    transactions = Transaction.objects.filter(
        source=source.get_owner(), destination=destination.get_owner(), accrual=accrual
    ).all()
    actual_source, actual_destination = _get_actual(source), _get_actual(destination)

    assert is_transfer != is_error
    assert actual_source.get_balance() == source_end
    assert actual_destination.get_balance() == destination_end
    assert len(transactions) == (1 if not is_error else 0)


def _get_actual(document: BankObject) -> BankObject:
    return (BankAccount if isinstance(document, BankAccount) else BankCard).objects.filter(pk=document.pk).first()
