from abc import ABC, abstractmethod
from decimal import Decimal

from django.db.models import QuerySet

from app.internal.bank.db.models import BankAccount
from app.internal.users.db.models import TelegramUser


class IBankAccountRepository(ABC):
    @abstractmethod
    def get_bank_accounts(self, user: TelegramUser) -> QuerySet[BankAccount]:
        pass

    @abstractmethod
    def accrue(self, account: BankAccount, accrual: Decimal) -> None:
        pass

    @abstractmethod
    def subtract(self, account: BankAccount, accrual: Decimal) -> None:
        pass
