from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Optional, Union

from django.db.models import QuerySet

from app.internal.bank.db.models import BankAccount
from app.internal.user.db.models import TelegramUser


class IBankAccountRepository(ABC):
    @abstractmethod
    def get_bank_account(self, user_id: int, number: int) -> Optional[BankAccount]:
        pass

    @abstractmethod
    def get_bank_accounts(self, user_id: Union[int, str]) -> QuerySet[BankAccount]:
        pass

    @abstractmethod
    def get_amount(self) -> int:
        pass

    @abstractmethod
    def accrue(self, number: int, accrual: Decimal) -> None:
        pass

    @abstractmethod
    def subtract(self, number: int, accrual: Decimal) -> None:
        pass

    @abstractmethod
    def get_user_bank_account_by_document_number(self, user_id: Union[int, str], number: int) -> Optional[BankAccount]:
        pass

    @abstractmethod
    def get_bank_account_by_document_number(self, number: int) -> Optional[BankAccount]:
        pass

    @abstractmethod
    def get_balance_total(self) -> Decimal:
        pass
