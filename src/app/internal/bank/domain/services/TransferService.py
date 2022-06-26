import logging.handlers
import uuid
from decimal import Decimal
from time import time
from typing import Optional

from django.conf import settings
from django.core.files.base import ContentFile
from django.db import IntegrityError
from django.db.transaction import atomic
from ninja import UploadedFile
from prometheus_client import Counter, Gauge, Summary

from app.internal.bank.db.models import BankAccount, BankObject, Transaction, TransactionTypes
from app.internal.bank.domain.interfaces import IBankAccountRepository, IBankCardRepository, ITransactionRepository
from app.internal.bank.domain.services.Photo import Photo

STARTING_LOG = "Starting transfer id={id} source={source} destination={destination} accrual={accrual} photo_size={size}"
SUBTRACTION_LOG = "Subtraction completed id={id}"
ACCRUAL_LOG = "Accrual completed id={id}"
SUCCESS_LOG = "Transfer completed id={id} duration={seconds}s"
INTEGRITY_LOG = "Transfer id={id} was not completed"
logger = logging.getLogger(__name__)

duration = Summary("transfer_duration", "")
accrual_sum = Counter("accrual_sum", "")
transfer_error = Counter("transfer_integrity_error", "")


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

    @duration.time()
    def try_transfer(
        self,
        source: BankAccount,
        destination: BankAccount,
        accrual: Decimal,
        photo: Optional[Photo],
    ) -> Optional[Transaction]:
        if not self.validate_accrual(accrual):
            raise ValueError()

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
        accrual_sum.inc(accrual.__float__())
        start = time()

        content = (
            ContentFile(content=photo.content, name=f"{photo.unique_name}.{self.PHOTO_EXTENSION}") if photo else None
        )
        try:
            with atomic():
                self._account_repo.subtract(source.number, accrual)
                logger.info(SUBTRACTION_LOG.format(id=id_))

                self._account_repo.accrue(destination.number, accrual)
                logger.info(ACCRUAL_LOG.format(id=id_))

                transaction = self._transaction_repo.declare(
                    source.number, destination.number, TransactionTypes.TRANSFER, accrual, content
                )

                seconds = round(time() - start, ndigits=3)
                message = SUCCESS_LOG.format(id=id_, seconds=seconds)
                (logger.info if seconds <= settings.MAX_TRANSFER_DURATION_SECONDS else logger.warning)(message)

                return transaction

        except IntegrityError:
            logger.error(INTEGRITY_LOG.format(id=id_))
            transfer_error.inc()

            return None
