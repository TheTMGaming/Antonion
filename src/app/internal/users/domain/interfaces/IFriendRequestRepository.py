from abc import ABC, abstractmethod
from typing import Optional

from app.internal.users.db.models import FriendRequest, TelegramUser


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
