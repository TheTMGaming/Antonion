from collections import Counter
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple

from django.conf import settings
from django.utils import timezone
from jwt import PyJWTError, decode, encode

from app.internal.authentication.db.models import RefreshToken
from app.internal.authentication.domain.interfaces import IAuthRepository
from app.internal.authentication.domain.services.TokenTypes import TokenTypes
from app.internal.users.db.models import TelegramUser


class JWTService:
    CREATED_AT = "created_at"
    TELEGRAM_ID = "telegram_id"
    TOKEN_TYPE = "type"
    PAYLOAD_FIELDS = [CREATED_AT, TELEGRAM_ID, TOKEN_TYPE]

    ALGORITHM = "HS256"

    def __init__(self, auth_repo: IAuthRepository):
        self._auth_repo = auth_repo

    def get_authenticated_telegram_user(self, payload: Dict[str, Any]) -> Optional[TelegramUser]:
        return self._auth_repo.get_authenticated_telegram_user(payload[self.TELEGRAM_ID])

    def get_refresh_token_from_db(self, value: str) -> Optional[RefreshToken]:
        return self._auth_repo.get_refresh_token_from_db(value)

    def create_access_and_refresh_tokens(self, user: TelegramUser) -> Tuple[str, str]:
        access = self.generate_token(user.id, TokenTypes.ACCESS)
        refresh = self.generate_token(user.id, TokenTypes.REFRESH)

        self._auth_repo.create_refresh_token(user, refresh)

        return access, refresh

    def update_access_and_refresh_tokens(self, refresh_token: RefreshToken) -> Optional[Tuple[str, str]]:
        if refresh_token.revoked:
            self._auth_repo.revoke_all_refresh_tokens(refresh_token.telegram_user)
            return None

        self._auth_repo.revoke_refresh_token(refresh_token)

        return self.create_access_and_refresh_tokens(refresh_token.telegram_user)

    def generate_token(self, telegram_id: int, token_type: TokenTypes) -> str:
        payload = {
            self.TOKEN_TYPE: token_type.value,
            self.TELEGRAM_ID: telegram_id,
            self.CREATED_AT: self._now().timestamp(),
        }

        return encode(payload, settings.SECRET_KEY, algorithm=self.ALGORITHM)

    def is_payload_valid(self, payload: Dict[str, Any]) -> bool:
        return bool(payload) and Counter(payload.keys()) == Counter(self.PAYLOAD_FIELDS)

    def try_get_payload(self, token: str) -> Dict[str, Any]:
        try:
            return decode(token, settings.SECRET_KEY, algorithms=[self.ALGORITHM])
        except PyJWTError:
            return {}

    def is_token_alive(self, payload: Dict[str, Any], token_type: TokenTypes, ttl: timedelta) -> bool:
        lifetime = self._now() - self._from_timestamp(float(payload[self.CREATED_AT]))

        return payload.get(self.TOKEN_TYPE) == token_type.value and lifetime < ttl

    @staticmethod
    def _now() -> datetime:
        return timezone.now()

    @staticmethod
    def _from_timestamp(value: float) -> datetime:
        return datetime.fromtimestamp(value, tz=timezone.get_current_timezone())
