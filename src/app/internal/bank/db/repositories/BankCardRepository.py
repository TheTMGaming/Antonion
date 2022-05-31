from typing import Optional, Union

from django.db.models import QuerySet

from app.internal.bank.db.models import BankCard
from app.internal.bank.domain.interfaces import IBankCardRepository


class BankCardRepository(IBankCardRepository):
    def get_card(self, user_id: Union[int, str], number: str) -> Optional[BankCard]:
        return BankCard.objects.filter(bank_account__owner_id=user_id, number=number).first()

    def get_cards(self, user_ud: Union[int, str]) -> QuerySet[BankCard]:
        return BankCard.objects.filter(bank_account__owner_id=user_ud).all()
