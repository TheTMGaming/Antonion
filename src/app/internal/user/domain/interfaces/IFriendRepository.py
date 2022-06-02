from abc import ABC, abstractmethod
from typing import Optional, Union

from django.db.models import QuerySet

from app.internal.user.db.models import TelegramUser


class IFriendRepository(ABC):
    @abstractmethod
    def get_friend(self, user_id: Union[int, str], identifier: Union[int, str]) -> Optional[TelegramUser]:
        pass

    @abstractmethod
    def get_friends(self, user_id: Union[int, str]) -> QuerySet[TelegramUser]:
        pass

    @abstractmethod
    def is_friend_exists(self, user_id: Union[int, str], friend_id: Union[int, str]) -> bool:
        pass

    @abstractmethod
    def remove(self, source: TelegramUser, friend: TelegramUser) -> None:
        pass
