from decimal import Decimal
from typing import Union

from django.db.models import F, QuerySet

from app.internal.bank.db.models import BankAccount
from app.internal.bank.domain.interfaces import IBankAccountRepository


class BankAccountRepository(IBankAccountRepository):
    def get_bank_account(self, number: int) -> BankAccount:
        return BankAccount.objects.filter(number=number).first()

    def get_bank_accounts(self, user_id: Union[int, str]) -> QuerySet[BankAccount]:
        return BankAccount.objects.filter(owner_id=user_id).all()

    def accrue(self, number: int, accrual: Decimal) -> None:
        BankAccount.objects.filter(number=number).update(balance=F("balance") + accrual)

    def subtract(self, number: int, accrual: Decimal) -> None:
        self.accrue(number, -accrual)
