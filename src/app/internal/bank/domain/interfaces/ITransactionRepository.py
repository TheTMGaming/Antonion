from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Iterable, Optional, Union

from django.core.files.base import ContentFile
from django.db.models import QuerySet

from app.internal.bank.db.models import Transaction, TransactionTypes


class ITransactionRepository(ABC):
    @abstractmethod
    def declare(
        self,
        source_number: int,
        destination_number: int,
        type_: TransactionTypes,
        accrual: Decimal,
        photo: Optional[ContentFile],
    ) -> Transaction:
        pass

    @abstractmethod
    def get_transactions(self, account_number: int) -> QuerySet[Transaction]:
        pass

    @abstractmethod
    def get_related_usernames(self, user_id: Union[int, str]) -> QuerySet[str]:
        pass

    @abstractmethod
    def get_new_transactions(self, user_id: Union[int, str]) -> QuerySet[Transaction]:
        pass

    @abstractmethod
    def mark_transactions_as_viewed(self, user_id: Union[int, str]) -> None:
        pass

    @abstractmethod
    def get_amount(self) -> int:
        pass
