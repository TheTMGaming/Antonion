from django.db.models import QuerySet

from app.internal.models.bank import BankAccount
from app.internal.models.user import TelegramUser


def get_bank_account(number: str) -> BankAccount:
    return BankAccount.objects.filter(number=number).first()


def get_bank_accounts(user: TelegramUser) -> QuerySet[BankAccount]:
    return BankAccount.objects.filter(owner=user.id).all()
