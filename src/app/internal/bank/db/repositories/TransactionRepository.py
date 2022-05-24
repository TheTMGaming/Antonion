from decimal import Decimal
from typing import Union

from django.core.exceptions import ValidationError
from django.db.models import Q, QuerySet

from app.internal.bank.db.models import BankAccount, Transaction, TransactionTypes
from app.internal.bank.domain.interfaces import ITransactionRepository


class TransactionRepository(ITransactionRepository):
    def declare(
        self, source: BankAccount, destination: BankAccount, type_: TransactionTypes, accrual: Decimal
    ) -> Transaction:
        if accrual < 0:
            raise ValidationError("Accrual must not be less than 0")

        return Transaction.objects.create(type=type_, source=source, destination=destination, accrual=accrual)

    def get_transactions(self, account: BankAccount) -> QuerySet[Transaction]:
        return Transaction.objects.filter(Q(source=account) | Q(destination=account)).all()

    def get_related_usernames(self, user_id: Union[int, str]) -> QuerySet[str]:
        from_ = Transaction.objects.filter(source__owner_id=user_id).values_list(
            "destination__owner__username", flat=True
        )
        to = Transaction.objects.filter(destination__owner_id=user_id).values_list("source__owner__username", flat=True)

        return from_.union(to)
