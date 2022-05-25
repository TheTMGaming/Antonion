from abc import ABC, abstractmethod
from typing import Optional, Union

from app.internal.users.db.models import TelegramUser


class ITelegramUserRepository(ABC):
    @abstractmethod
    def try_add_or_update_user(self, user_id: Union[int, str], username: str, first_name: str, last_name: str) -> bool:
        pass

    @abstractmethod
    def get_user(self, identifier: Union[int, str]) -> Optional[TelegramUser]:
        pass

    @abstractmethod
    def update_phone(self, user_id: Union[int, str], value: str) -> None:
        pass

    @abstractmethod
    def update_password(self, user_id: Union[int, str], value: str) -> None:
        pass
