from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Union

from django.db.models import QuerySet

from app.internal.bank.db.models import BankAccount
from app.internal.users.db.models import TelegramUser


class IBankAccountRepository(ABC):
    @abstractmethod
    def get_bank_account(self, number: int) -> BankAccount:
        pass

    @abstractmethod
    def get_bank_accounts(self, user_id: Union[int, str]) -> QuerySet[BankAccount]:
        pass

    @abstractmethod
    def accrue(self, number: int, accrual: Decimal) -> None:
        pass

    @abstractmethod
    def subtract(self, number: int, accrual: Decimal) -> None:
        pass
