from abc import ABC, abstractmethod
from decimal import Decimal

from app.internal.bank.db.models import BankAccount, Transaction, TransactionTypes


class ITransactionRepository(ABC):
    @abstractmethod
    def declare(
        self, source: BankAccount, destination: BankAccount, type_: TransactionTypes, accrual: Decimal
    ) -> Transaction:
        pass
