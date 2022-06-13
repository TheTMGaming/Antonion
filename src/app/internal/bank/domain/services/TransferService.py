from decimal import Decimal
from typing import Optional, Union

from django.core.files.base import ContentFile
from django.db import IntegrityError, transaction
from telegram import Document, PhotoSize, TelegramError

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

    def try_transfer(
        self,
        source: BankAccount,
        destination: BankAccount,
        accrual: Decimal,
        photo: Optional[Union[PhotoSize, Document]],
    ) -> Optional[Transaction]:
        if not self.validate_accrual(accrual):
            raise ValueError()

        try:
            if photo:
                photo = ContentFile(content=photo.get_file().download_as_bytearray(), name=photo.file_unique_id)
        except TelegramError:
            return None

        try:
            with transaction.atomic():
                self._account_repo.subtract(source.number, accrual)
                self._account_repo.accrue(destination.number, accrual)

            return self._transaction_repo.declare(
                source.number, destination.number, TransactionTypes.TRANSFER, accrual, photo
            )

        except IntegrityError:
            return None
