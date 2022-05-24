from abc import ABC, abstractmethod
from typing import Optional

from app.internal.authentication.db.models import RefreshToken
from app.internal.users.db.models import TelegramUser


class IAuthRepository(ABC):
    @abstractmethod
    def get_refresh_token_from_db(self, value: str) -> Optional[RefreshToken]:
        pass

    @abstractmethod
    def create_refresh_token(self, user: TelegramUser, value: str) -> None:
        pass

    @abstractmethod
    def revoke_all_refresh_tokens(self, user: TelegramUser) -> None:
        pass

    @abstractmethod
    def revoke_refresh_token(self, token: RefreshToken) -> None:
        pass

    @abstractmethod
    def get_authenticated_telegram_user(self, telegram_id: int) -> Optional[TelegramUser]:
        pass
