from typing import Optional

from django.conf import settings
from django.http import HttpRequest, HttpResponse

from app.internal.authentication.TokenTypes import TokenTypes
from app.internal.authentication.utils import (
    get_authenticated_telegram_user,
    is_payload_valid,
    is_token_alive,
    try_get_payload,
)


class JWTAuthenticationMiddleware:
    TOKEN_HEADER = "Authorization"
    BEARER = "bearer"

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        request.telegram_user = None

        token = self._get_bearer_token(request)
        if not token:
            return self.get_response(request)

        payload = try_get_payload(token)
        if is_payload_valid(payload) and is_token_alive(payload, TokenTypes.ACCESS, settings.ACCESS_TOKEN_TTL):
            request.telegram_user = get_authenticated_telegram_user(payload)

        return self.get_response(request)

    def _get_bearer_token(self, request: HttpRequest) -> Optional[str]:
        parameters = request.headers.get(self.TOKEN_HEADER, "").split()

        if len(parameters) != 2 or parameters[0].lower() != self.BEARER:
            return None

        return parameters[1]
