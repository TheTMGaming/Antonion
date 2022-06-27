from abc import ABC, abstractmethod
from typing import Optional, Union

from django.db.models import QuerySet

from app.internal.bank.db.models import BankCard
from app.internal.user.db.models import TelegramUser


class IBankCardRepository(ABC):
    @abstractmethod
    def get_card(self, user_id: Union[int, str], number: int) -> Optional[BankCard]:
        pass

    @abstractmethod
    def get_cards(self, user_id: Union[int, str]) -> QuerySet[BankCard]:
        pass

    @abstractmethod
    def get_amount(self) -> int:
        pass
