from decimal import Decimal
from typing import List

import pytest
from django.core.exceptions import ValidationError

from app.internal.models.bank import TransactionTypes
from app.internal.models.user import TelegramUser
from app.internal.services.bank.transaction import declare_transaction


@pytest.mark.django_db
def test_transaction_declaration(telegram_users: List[TelegramUser]) -> None:
    source, destination = telegram_users[:2]

    for accrual in map(Decimal, range(-1, 2)):
        if accrual < 0:
            with pytest.raises(ValidationError):
                declare_transaction(source, destination, TransactionTypes.TRANSFER, accrual)
        else:
            transaction = declare_transaction(source, destination, TransactionTypes.TRANSFER, accrual)
            assert transaction.source == source
            assert transaction.destination == destination
            assert transaction.accrual == accrual

