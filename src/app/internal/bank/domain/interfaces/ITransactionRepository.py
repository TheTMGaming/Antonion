from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Union

from django.db.models import QuerySet

from app.internal.bank.db.models import BankAccount, Transaction, TransactionTypes


class ITransactionRepository(ABC):
    @abstractmethod
    def declare(
        self, source_number: int, destination_number: int, type_: TransactionTypes, accrual: Decimal
    ) -> Transaction:
        pass

    @abstractmethod
    def get_transactions(self, account_number: int) -> QuerySet[Transaction]:
        pass

    @abstractmethod
    def get_related_usernames(self, user_id: Union[int, str]) -> QuerySet[str]:
        pass
