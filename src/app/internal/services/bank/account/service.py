from django.db.models import QuerySet

from app.internal.models.bank import BankAccount, BankCard, BankObject
from app.internal.models.user import TelegramUser


def get_bank_account(number: str) -> BankAccount:
    return BankAccount.objects.filter(number=number).first()


def get_bank_accounts(user: TelegramUser) -> QuerySet[BankAccount]:
    return user.bank_accounts.all()


def get_bank_account_from_document(document: BankObject) -> BankAccount:
    if isinstance(document, BankAccount):
        return document

    if isinstance(document, BankCard):
        return document.bank_account

    raise ValueError()
