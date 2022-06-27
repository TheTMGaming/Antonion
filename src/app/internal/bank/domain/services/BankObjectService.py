from itertools import chain
from typing import Optional

from django.db.models import QuerySet
from prometheus_client import Gauge

from app.internal.bank.db.models import BankAccount, BankCard, BankObject
from app.internal.bank.domain.interfaces import IBankAccountRepository, IBankCardRepository
from app.internal.user.db.models import TelegramUser


class BankObjectService:
    ACCOUNT_AMOUNT = Gauge("account_amount", "")
    CARD_AMOUNT = Gauge("card_amount", "")
    BALANCE_TOTAL = Gauge("balance_total", "")

    def __init__(self, account_repo: IBankAccountRepository, card_repo: IBankCardRepository):
        self._account_repo = account_repo
        self._card_repo = card_repo

        self.ACCOUNT_AMOUNT.set_function(self._account_repo.get_amount)
        self.CARD_AMOUNT.set_function(self._card_repo.get_amount)
        self.BALANCE_TOTAL.set_function(lambda: self._account_repo.get_balance_total().__float__())

    def get_bank_account_from_document(self, document: BankObject) -> BankAccount:
        if isinstance(document, BankAccount):
            return document

        if isinstance(document, BankCard):
            return document.bank_account

        raise ValueError()

    def get_documents_order(self, user: TelegramUser) -> dict:
        return dict(
            (number, document)
            for number, document in enumerate(
                chain(self._account_repo.get_bank_accounts(user.id), self._card_repo.get_cards(user.id)), start=1
            )
        )

    def is_balance_zero(self, document: BankObject) -> bool:
        return document.get_balance() == 0

    def get_bank_accounts(self, user: TelegramUser) -> QuerySet[BankAccount]:
        return self._account_repo.get_bank_accounts(user.id)

    def get_bank_account(self, user: TelegramUser, number: int) -> Optional[BankAccount]:
        return self._account_repo.get_bank_account(user.id, number)

    def get_cards(self, user: TelegramUser) -> QuerySet[BankCard]:
        return self._card_repo.get_cards(user.id)

    def get_card(self, user: TelegramUser, number: int) -> Optional[BankCard]:
        return self._card_repo.get_card(user.id, number)

    def get_user_bank_account_by_document_number(self, user: TelegramUser, number: int) -> Optional[BankAccount]:
        return self._account_repo.get_user_bank_account_by_document_number(user.id, number)

    def get_bank_account_by_document_number(self, number) -> Optional[BankAccount]:
        return self._account_repo.get_bank_account_by_document_number(number)
