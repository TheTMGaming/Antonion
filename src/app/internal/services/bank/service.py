from decimal import Decimal, getcontext
from itertools import chain
from typing import List, Union

from django.db.models import QuerySet

from app.internal.models.bank import BankAccount, BankCard, BankObject, Transaction, TransactionTypes
from app.internal.models.user import TelegramUser


def get_card(number: str) -> BankCard:
    return BankCard.objects.filter(number=number).first()


def get_cards(user: TelegramUser) -> List[BankCard]:
    return list(card for account in get_bank_accounts(user) for card in account.bank_cards.all())


def get_bank_account(number: str) -> BankAccount:
    return BankAccount.objects.filter(number=number).first()


def get_bank_accounts(user: TelegramUser) -> QuerySet[BankAccount]:
    return BankAccount.objects.filter(owner=user.id).all()


def confirm_card(card: BankCard, user_id: int) -> bool:
    return confirm_bank_account(card.bank_account, user_id)


def confirm_bank_account(account: BankAccount, user_id: int) -> bool:
    return account.owner.id == user_id


def validate_card_number(number: str) -> bool:
    return _validate_number(number, BankCard.DIGITS_COUNT)


def validate_bank_account_number(number: str) -> bool:
    return _validate_number(number, BankAccount.DIGITS_COUNT)


def _validate_number(number: str, length: int) -> bool:
    return number.isdigit() and len(number) == length


def get_documents_with_enums(user: TelegramUser) -> dict:
    return dict(
        (number, document) for number, document in enumerate(chain(get_bank_accounts(user), get_cards(user)), start=1)
    )


def parse_accrual(message: str) -> Decimal:
    return Decimal(round(Decimal(message), 2))


def try_transfer(source: BankObject, destination: BankObject, accrual: Decimal) -> bool:
    is_extract = source.try_extract(accrual)
    is_add = destination.try_add(accrual)

    if is_extract and is_add:
        source.save_operation()
        destination.save_operation()

        declare_transaction(source.get_owner(), destination.get_owner(), TransactionTypes.TRANSFER, accrual)

        return True

    return False


def declare_transaction(
    source: TelegramUser, destination: TelegramUser, type_: TransactionTypes, accrual: Decimal
) -> Transaction:
    return Transaction.objects.create(type=type_, source=source, destination=destination, accrual=accrual)
