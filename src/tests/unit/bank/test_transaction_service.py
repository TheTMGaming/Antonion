from decimal import Decimal
from typing import List

import pytest
from django.core.exceptions import ValidationError

from app.internal.bank.db.models import BankAccount, Transaction, TransactionTypes
from app.internal.general.services import transaction_service


@pytest.mark.django_db
@pytest.mark.unit
def test_transaction_declaration(bank_accounts: List[BankAccount]) -> None:
    source, destination = bank_accounts[:2]

    for accrual in map(Decimal, range(-1, 2)):
        if accrual < 0:
            with pytest.raises(ValidationError):
                transaction_service.declare(source, destination, TransactionTypes.TRANSFER, accrual)
        else:
            transaction = transaction_service.declare(source, destination, TransactionTypes.TRANSFER, accrual)
            assert transaction.source == source
            assert transaction.destination == destination
            assert transaction.accrual == accrual


@pytest.mark.django_db
@pytest.mark.unit
def test_getting_usernames_of_relations(bank_account: BankAccount, friend_accounts: List[BankAccount]) -> None:
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
