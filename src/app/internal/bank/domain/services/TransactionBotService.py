from decimal import Decimal
from typing import Union

from django.db.models import QuerySet

from app.internal.bank.db.models import BankAccount, Transaction, TransactionTypes
from app.internal.bank.domain.interfaces import ITransactionRepository
from app.internal.users.db.models import TelegramUser


class TransactionBotService:
    def __init__(self, transaction_repo: ITransactionRepository):
        self._transaction_repo = transaction_repo

    def declare(
        self, source: BankAccount, destination: BankAccount, type_: TransactionTypes, accrual: Decimal
    ) -> Transaction:
        return self._transaction_repo.declare(source.number, destination.number, type_, accrual)

    def get_transactions(self, account: BankAccount) -> QuerySet[Transaction]:
        return self._transaction_repo.get_transactions(account.number)

    def get_related_usernames(self, user_id: Union[int, str]) -> QuerySet[str]:
        return self._transaction_repo.get_related_usernames(user_id)
