from abc import ABC, abstractmethod
from typing import Union

from django.db.models import QuerySet

from app.internal.users.db.models import TelegramUser


class IFriendRepository(ABC):
    @abstractmethod
    def get_friends(self, user_id: Union[int, str]) -> QuerySet[TelegramUser]:
        pass
