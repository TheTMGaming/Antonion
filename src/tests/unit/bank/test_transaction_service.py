import os
from decimal import Decimal
from typing import Iterable, List

import pytest
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile

from app.internal.bank.db.models import BankAccount, Transaction, TransactionTypes
from app.internal.general.services import transaction_service


@pytest.mark.django_db
@pytest.mark.unit
def test_declaration(bank_accounts: List[BankAccount]) -> None:
    source, destination = bank_accounts[:2]

    for accrual in map(Decimal, range(-1, 2)):
        content = bytearray(os.urandom(10))
        photo = ContentFile(content=content, name=str(accrual))

        if accrual < 0:
            with pytest.raises(ValidationError):
                transaction_service.declare(source, destination, TransactionTypes.TRANSFER, accrual, photo)
        else:
            transaction = transaction_service.declare(source, destination, TransactionTypes.TRANSFER, accrual, photo)
            assert transaction.source == source
            assert transaction.destination == destination
            assert transaction.accrual == accrual
            assert transaction.photo.read() == content

            transaction.delete()


@pytest.mark.django_db
@pytest.mark.unit
def test_getting_related_usernames(bank_account: BankAccount, friend_accounts: List[BankAccount]) -> None:
    half = len(friend_accounts) // 2
    Transaction.objects.bulk_create(
        Transaction(source=bank_account, destination=another) for another in friend_accounts[:half]
    )
    Transaction.objects.bulk_create(
        Transaction(source=another, destination=bank_account) for another in friend_accounts[half:]
    )

    actual = sorted(transaction_service.get_related_usernames(bank_account.owner.id))
    expected = sorted(account.owner.username for account in friend_accounts)

    assert actual == expected


@pytest.mark.django_db
@pytest.mark.unit
def test_getting_and_marking_new_transactions(bank_account: BankAccount, another_account: BankAccount) -> None:
    expected = Transaction.objects.bulk_create(
        [Transaction(source=bank_account, destination=another_account) for _ in range(3)]
        + [Transaction(source=another_account, destination=bank_account) for _ in range(3)]
    )

    transactions = transaction_service.get_and_mark_new_transactions(bank_account.owner)
    assert_getting_and_marking_new_transactions(transactions, expected, bank_account)

    transactions = transaction_service.get_and_mark_new_transactions(another_account.owner)
    filtered = [
        transaction
        for transaction in expected
        if transaction.source.owner == another_account.owner or transaction.destination.owner == another_account.owner
    ]
    assert_getting_and_marking_new_transactions(transactions, filtered, another_account)


def assert_getting_and_marking_new_transactions(
    actual: Iterable[Transaction], expected: Iterable[Transaction], bank_account: BankAccount
) -> None:
    assert sorted(actual, key=str) == sorted(expected, key=str)
    assert not Transaction.objects.filter(source__owner_id=bank_account.owner.id, was_source_viewed=False).exists()
    assert not Transaction.objects.filter(
        destination__owner__id=bank_account.owner.id, was_destination_viewed=False
    ).exists()
