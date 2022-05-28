from abc import ABC, abstractmethod
from typing import Optional, Union

from django.db.models import QuerySet

from app.internal.user.db.models import FriendRequest, TelegramUser


class IFriendRequestRepository(ABC):
    @abstractmethod
    def create(self, source: TelegramUser, destination: TelegramUser) -> FriendRequest:
        pass

    @abstractmethod
    def get(self, source: TelegramUser, destination: TelegramUser) -> Optional[FriendRequest]:
        pass

    @abstractmethod
    def exists(self, source: TelegramUser, destination: TelegramUser) -> bool:
        pass

    @abstractmethod
    def remove(self, source: TelegramUser, destination: TelegramUser) -> bool:
        pass

    @abstractmethod
    def get_usernames_to_friends(self, user_id: Union[int, str]) -> QuerySet[str]:
        pass
