from typing import Optional

from django.conf import settings
from django.http import HttpRequest
from ninja.security import HttpBearer

from app.internal.authentication.db.repositories import AuthRepository
from app.internal.authentication.domain.services import JWTService
from app.internal.authentication.domain.services.TokenTypes import TokenTypes
from app.internal.user.db.repositories import TelegramUserRepository


class JWTAuthentication(HttpBearer):
    _service = JWTService(auth_repo=AuthRepository(), user_repo=TelegramUserRepository())

    def authenticate(self, request: HttpRequest, token: str) -> Optional[str]:
        request.telegram_user = None

        payload = self._service.try_get_payload(token)

        if self._service.is_payload_valid(payload) and self._service.is_token_alive(
            payload, TokenTypes.ACCESS, settings.ACCESS_TOKEN_TTL
        ):
            request.telegram_user = self._service.get_authenticated_telegram_user(payload)

            return token if request.telegram_user is not None else None

        return None
