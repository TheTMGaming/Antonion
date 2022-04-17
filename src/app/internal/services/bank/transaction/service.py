from decimal import Decimal

from django.core.exceptions import ValidationError

from app.internal.models.bank import Transaction, TransactionTypes
from app.internal.models.user import TelegramUser


def declare_transaction(
    source: TelegramUser, destination: TelegramUser, type_: TransactionTypes, accrual: Decimal
) -> Transaction:
    if accrual < 0:
        raise ValidationError("Accrual must not be less than 0")

    return Transaction.objects.create(type=type_, source=source, destination=destination, accrual=accrual)
