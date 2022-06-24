import logging.handlers
import uuid
from decimal import Decimal
from time import time
from typing import Callable, Optional

from django.conf import settings
from django.core.files.base import ContentFile
from django.db import IntegrityError
from django.db.transaction import atomic
from ninja import UploadedFile

from app.internal.bank.db.models import BankAccount, BankObject, Transaction, TransactionTypes
from app.internal.bank.domain.interfaces import IBankAccountRepository, IBankCardRepository, ITransactionRepository
from app.internal.bank.domain.services.Photo import Photo

STARTING_LOG = "Starting transfer id={id} source={source} destination={destination} accrual={accrual} photo_size={size}"
SUCCESS_LOG = "Transfer completed id={id} duration={seconds}s"
INTEGRITY_LOG = "Transfer id={id} was not completed"
logger = logging.getLogger()


def log(try_transfer: Callable) -> Callable:
    def wrapper(
        instance: "TransferService",
        source: BankAccount,
        destination: BankAccount,
        accrual: Decimal,
        photo: Optional[Photo],
    ) -> Optional[Transaction]:
        id_ = uuid.uuid4()
        logger.info(
            STARTING_LOG.format(
                id=id_,
                source=source.pretty_number,
                destination=destination.pretty_number,
                accrual=accrual,
                size=photo.size if photo else None,
            )
        )
        start = time()

        transaction = try_transfer(instance, source, destination, accrual, photo)

        if not transaction:
            logger.error(INTEGRITY_LOG.format(id=id_))
        else:
            seconds = round(time() - start, ndigits=3)
            message = SUCCESS_LOG.format(id=id_, seconds=seconds)
            (logger.info if seconds <= settings.MAX_OPERATION_SECONDS else logger.warning)(message)

        return transaction

    return wrapper


class TransferService:
    PHOTO_EXTENSION = "jpg"

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

    def validate_file(self, file: UploadedFile) -> bool:
        return file is None or file.content_type.startswith("image") and file.size <= settings.MAX_SIZE_PHOTO_BYTES

    def parse_accrual(self, digits: str) -> Decimal:
        accrual = Decimal(round(Decimal(digits), BankAccount.DECIMAL_PLACES))

        if not self.validate_accrual(accrual):
            raise ValueError()

        return accrual

    def can_extract_from(self, document: BankObject, accrual: Decimal) -> bool:
        if not self.validate_accrual(accrual):
            raise ValueError()

        return accrual <= document.get_balance()

    @log
    def try_transfer(
        self,
        source: BankAccount,
        destination: BankAccount,
        accrual: Decimal,
        photo: Optional[Photo],
    ) -> Optional[Transaction]:
        if not self.validate_accrual(accrual):
            raise ValueError()

        content = (
            ContentFile(content=photo.content, name=f"{photo.unique_name}.{self.PHOTO_EXTENSION}") if photo else None
        )
        try:
            with atomic():
                self._account_repo.subtract(source.number, accrual)
                self._account_repo.accrue(destination.number, accrual)

                return self._transaction_repo.declare(
                    source.number, destination.number, TransactionTypes.TRANSFER, accrual, content
                )

        except IntegrityError:
            return None
