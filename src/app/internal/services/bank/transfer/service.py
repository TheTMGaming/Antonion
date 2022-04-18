from decimal import Decimal
from itertools import chain

from django.db import IntegrityError, transaction

from app.internal.models.bank import BankAccount, BankObject, TransactionTypes
from app.internal.models.user import TelegramUser
from app.internal.services.bank.account import get_bank_accounts
from app.internal.services.bank.card import get_cards
from app.internal.services.bank.transaction import declare_transaction


def get_documents_with_enums(user: TelegramUser) -> dict:
    return dict(
        (number, document) for number, document in enumerate(chain(get_bank_accounts(user), get_cards(user)), start=1)
    )


def is_balance_zero(document: BankObject) -> bool:
    return document.get_balance() == 0


def validate_accrual(value: Decimal) -> bool:
    info = value.as_tuple()
    amount_before = len(info.digits) + info.exponent

    return value > 0 and amount_before <= BankAccount.DIGITS_COUNT and abs(info.exponent) <= BankAccount.DECIMAL_PLACES


def parse_accrual(digits: str) -> Decimal:
    accrual = Decimal(round(Decimal(digits), BankAccount.DECIMAL_PLACES))

    if not validate_accrual(accrual):
        raise ValueError()

    return accrual


def can_extract_from(document: BankObject, accrual: Decimal) -> bool:
    if not validate_accrual(accrual):
        raise ValueError()

    return accrual <= document.get_balance()


def try_transfer(source: BankObject, destination: BankObject, accrual: Decimal) -> bool:
    if not validate_accrual(accrual):
        raise ValueError()

    is_extract = source.try_extract(accrual)
    is_add = destination.try_add(accrual)

    if is_extract and is_add:
        try:
            with transaction.atomic():
                source.save_operation()
                destination.save_operation()

            declare_transaction(source.get_owner(), destination.get_owner(), TransactionTypes.TRANSFER, accrual)

            return True

        except IntegrityError:
            return False

    return False
