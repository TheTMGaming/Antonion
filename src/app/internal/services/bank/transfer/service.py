from decimal import Decimal
from itertools import chain

from django.db import IntegrityError, transaction
from django.db.models import F

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


def try_transfer(source: BankAccount, destination: BankAccount, accrual: Decimal) -> bool:
    if not validate_accrual(accrual):
        raise ValueError()

    try:
        with transaction.atomic():
            source.balance = F("balance") - accrual
            destination.balance = F("balance") + accrual

            source.save(update_fields=("balance",))
            destination.save(update_fields=("balance",))

        declare_transaction(source, destination, TransactionTypes.TRANSFER, accrual)

        return True

    except IntegrityError:
        return False
