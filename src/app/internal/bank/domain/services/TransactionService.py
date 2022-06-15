from decimal import Decimal
from typing import List, Optional, Union

from django.core.files.base import ContentFile
from django.db.models import QuerySet
from telegram import User

from app.internal.bank.db.models import BankAccount, Transaction, TransactionTypes
from app.internal.bank.domain.interfaces import ITransactionRepository
from app.internal.user.db.models import TelegramUser


class TransactionService:
    def __init__(self, transaction_repo: ITransactionRepository):
        self._transaction_repo = transaction_repo

    def declare(
        self,
        source: BankAccount,
        destination: BankAccount,
        type_: TransactionTypes,
        accrual: Decimal,
        photo: Optional[ContentFile],
    ) -> Transaction:
        return self._transaction_repo.declare(source.number, destination.number, type_, accrual, photo)

    def get_transactions(self, account: BankAccount) -> QuerySet[Transaction]:
        return self._transaction_repo.get_transactions(account.number)

    def get_related_usernames(self, user_id: Union[int, str]) -> QuerySet[str]:
        return self._transaction_repo.get_related_usernames(user_id)

    def get_and_mark_new_transactions(self, user: Union[User, TelegramUser]) -> List[Transaction]:
        transactions = list(self._transaction_repo.get_new_transactions(user.id))

        self._transaction_repo.mark_transactions_as_viewed(user.id)

        return transactions
