from decimal import Decimal

from app.internal.models.bank import Transaction, TransactionTypes
from app.internal.models.user import TelegramUser


def declare_transaction(
    source: TelegramUser, destination: TelegramUser, type_: TransactionTypes, accrual: Decimal
) -> Transaction:
    return Transaction.objects.create(type=type_, source=source, destination=destination, accrual=accrual)
