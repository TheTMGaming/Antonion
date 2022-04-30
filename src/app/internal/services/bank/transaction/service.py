from collections import namedtuple
from decimal import Decimal
from typing import Iterable, NamedTuple, Tuple

from django.core.exceptions import ValidationError
from django.db.models import Q, QuerySet

from app.internal.models.bank import BankAccount, Transaction, TransactionTypes

SeparatedTransactions = namedtuple("SeparatedTransactions", ["to", "me"])


def declare_transaction(
    source: BankAccount, destination: BankAccount, type_: TransactionTypes, accrual: Decimal
) -> Transaction:
    if accrual < 0:
        raise ValidationError("Accrual must not be less than 0")

    return Transaction.objects.create(type=type_, source=source, destination=destination, accrual=accrual)


def get_transactions(account: BankAccount) -> QuerySet[Transaction]:
    return Transaction.objects.filter(Q(source=account) | Q(destination=account)).all()


def separate_transfer_transactions(account: BankAccount, transactions: Iterable[Transaction]) -> SeparatedTransactions:
    to, from_ = [], []
    for transaction in transactions:
        (from_ if transaction.source == account else to).append(transaction)

    return SeparatedTransactions(to, from_)
