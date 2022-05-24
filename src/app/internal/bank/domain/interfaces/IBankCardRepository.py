from abc import ABC, abstractmethod

from django.db.models import QuerySet

from app.internal.bank.db.models import BankCard
from app.internal.users.db.models import TelegramUser


class IBankCardRepository(ABC):
    @abstractmethod
    def get_cards(self, user: TelegramUser) -> QuerySet[BankCard]:
        pass
