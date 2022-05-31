from decimal import Decimal
from typing import Optional

from django.db import IntegrityError, transaction

from app.internal.bank.db.models import BankAccount, BankObject, Transaction, TransactionTypes
from app.internal.bank.domain.interfaces import IBankAccountRepository, IBankCardRepository, ITransactionRepository


class TransferService:
    def __init__(
        self,
        account_repo: IBankAccountRepository,
        card_repo: IBankCardRepository,
        transaction_repo: ITransactionRepository,
    ):
        self._account_repo = account_repo
        self._card_repo = card_repo
        self._transaction_repo = transaction_repo

    def is_balance_zero(self, document: BankObject) -> bool:
        return document.get_balance() == 0

    def validate_accrual(self, value: Decimal) -> bool:
        info = value.as_tuple()
        amount_before = len(info.digits) + info.exponent

        return (
            value > 0 and amount_before <= BankAccount.DIGITS_COUNT and abs(info.exponent) <= BankAccount.DECIMAL_PLACES
        )

    def parse_accrual(self, digits: str) -> Decimal:
        accrual = Decimal(round(Decimal(digits), BankAccount.DECIMAL_PLACES))

        if not self.validate_accrual(accrual):
            raise ValueError()

        return accrual

    def can_extract_from(self, document: BankObject, accrual: Decimal) -> bool:
        if not self.validate_accrual(accrual):
            raise ValueError()

        return accrual <= document.get_balance()

    def try_transfer(self, source: BankAccount, destination: BankAccount, accrual: Decimal) -> Optional[Transaction]:
        if not self.validate_accrual(accrual):
            raise ValueError()

        try:
            with transaction.atomic():
                self._account_repo.subtract(source.number, accrual)
                self._account_repo.accrue(destination.number, accrual)

            return self._transaction_repo.declare(source.number, destination.number, TransactionTypes.TRANSFER, accrual)

        except IntegrityError:
            return None
