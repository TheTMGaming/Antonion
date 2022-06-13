from decimal import Decimal
from typing import Optional, Union

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db.models import Q, QuerySet

from app.internal.bank.db.models import Transaction, TransactionTypes
from app.internal.bank.domain.interfaces import ITransactionRepository


class TransactionRepository(ITransactionRepository):
    def declare(
        self,
        source_number: int,
        destination_number: int,
        type_: TransactionTypes,
        accrual: Decimal,
        photo: Optional[ContentFile],
    ) -> Transaction:
        if accrual < 0:
            raise ValidationError("Accrual must not be less than 0")

        return Transaction.objects.create(
            type=type_,
            source_id=source_number,
            destination_id=destination_number,
            accrual=accrual,
            photo=photo,
        )

    def get_transactions(self, account_number: int) -> QuerySet[Transaction]:
        return Transaction.objects.filter(
            Q(source__number=account_number) | Q(destination__number=account_number)
        ).all()

    def get_related_usernames(self, user_id: Union[int, str]) -> QuerySet[str]:
        from_ = Transaction.objects.filter(source__owner_id=user_id).values_list(
            "destination__owner__username", flat=True
        )
        to = Transaction.objects.filter(destination__owner_id=user_id).values_list("source__owner__username", flat=True)

        return from_.union(to)

    def get_new_transactions(self, user_id: Union[int, str]) -> QuerySet[Transaction]:
        return Transaction.objects.filter(
            Q(source__owner_id=user_id) & Q(was_source_viewed=False)
            | Q(destination__owner__id=user_id) & Q(was_destination_viewed=False)
        )

    def mark_transactions_as_viewed(self, user_id: Union[int, str]) -> None:
        Transaction.objects.filter(source__owner_id=user_id).update(was_source_viewed=True)
        Transaction.objects.filter(destination__owner_id=user_id).update(was_destination_viewed=True)
