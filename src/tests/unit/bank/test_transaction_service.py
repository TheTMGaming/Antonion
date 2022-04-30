from decimal import Decimal
from typing import List

import pytest
from django.core.exceptions import ValidationError

from app.internal.models.bank import BankAccount, TransactionTypes
from app.internal.services.bank.transaction import declare_transaction


@pytest.mark.django_db
@pytest.mark.unit
def test_transaction_declaration(bank_accounts: List[BankAccount]) -> None:
    source, destination = bank_accounts[:2]

    for accrual in map(Decimal, range(-1, 2)):
        if accrual < 0:
            with pytest.raises(ValidationError):
                declare_transaction(source, destination, TransactionTypes.TRANSFER, accrual)
        else:
            transaction = declare_transaction(source, destination, TransactionTypes.TRANSFER, accrual)
            assert transaction.source == source
            assert transaction.destination == destination
            assert transaction.accrual == accrual
