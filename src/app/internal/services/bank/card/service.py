from typing import Optional

from django.db.models import QuerySet

from app.internal.models.bank import BankCard
from app.internal.models.user import TelegramUser


def get_card(number: str) -> Optional[BankCard]:
    return BankCard.objects.filter(number=number).first()


def get_cards(user: TelegramUser) -> QuerySet[BankCard]:
    return BankCard.objects.filter(bank_account__owner=user).all()
