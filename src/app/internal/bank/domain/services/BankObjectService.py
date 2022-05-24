from itertools import chain

from app.internal.bank.db.models import BankAccount, BankCard, BankObject
from app.internal.bank.domain.interfaces import IBankAccountRepository, IBankCardRepository
from app.internal.users.db.models import TelegramUser


class BankObjectService:
    def __init__(self, account_repo: IBankAccountRepository, card_repo: IBankCardRepository):
        self._account_repo = account_repo
        self._card_repo = card_repo

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
                chain(self._account_repo.get_bank_accounts(user), self._card_repo.get_cards(user)), start=1
            )
        )

    def is_balance_zero(self, document: BankObject) -> bool:
        return document.get_balance() == 0
