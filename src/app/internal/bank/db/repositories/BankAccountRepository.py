from decimal import Decimal
from typing import Optional, Union

from django.db.models import F, Q, QuerySet

from app.internal.bank.db.models import BankAccount
from app.internal.bank.domain.interfaces import IBankAccountRepository


class BankAccountRepository(IBankAccountRepository):
    def get_bank_account(self, user_id: int, number: int) -> Optional[BankAccount]:
        return BankAccount.objects.filter(owner_id=user_id, number=number).first()

    def get_bank_accounts(self, user_id: Union[int, str]) -> QuerySet[BankAccount]:
        return BankAccount.objects.filter(owner_id=user_id).all()

    def accrue(self, number: int, accrual: Decimal) -> None:
        BankAccount.objects.filter(number=number).update(balance=F("balance") + accrual)

    def subtract(self, number: int, accrual: Decimal) -> None:
        self.accrue(number, -accrual)

    def get_bank_account_by_document_number(self, number: int) -> Optional[BankAccount]:
        return self._get_by_document_number(number).first()

    def get_user_bank_account_by_document_number(self, user_id: Union[int, str], number: int) -> Optional[BankAccount]:
        return self._get_by_document_number(number).filter(owner_id=user_id).first()

    def _get_by_document_number(self, number: int) -> QuerySet[BankAccount]:
        return BankAccount.objects.filter(Q(number=number) | Q(bank_cards__number=number))
