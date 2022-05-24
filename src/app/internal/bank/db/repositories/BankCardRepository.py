from typing import Optional

from django.db.models import QuerySet

from app.internal.bank.db.models import BankCard
from app.internal.bank.domain.interfaces import IBankCardRepository
from app.internal.users.db.models import TelegramUser


class BankCardRepository(IBankCardRepository):
    def get_card(self, number: str) -> Optional[BankCard]:
        return BankCard.objects.filter(number=number).first()

    def get_cards(self, user: TelegramUser) -> QuerySet[BankCard]:
        return BankCard.objects.filter(bank_account__owner=user).all()
