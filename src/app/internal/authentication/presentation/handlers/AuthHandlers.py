from django.conf import settings
from django.http import HttpRequest
from ninja import Body
from ninja.responses import Response

from app.internal.authentication.domain.entities import AccessTokenOut, CredentialsSchema
from app.internal.authentication.domain.services import JWTService
from app.internal.authentication.domain.services.TokenTypes import TokenTypes
from app.internal.general.rest.exceptions import (
    AccessTokenTTLZeroException,
    InvalidPayloadException,
    RevokedRefreshTokenException,
    UnauthorizedException,
    UndefinedRefreshTokenException,
    UnknownRefreshTokenException,
)


class AuthHandlers:
    def __init__(self, auth_service: JWTService):
        self._auth_service = auth_service

    def login(self, request: HttpRequest, credentials: CredentialsSchema = Body(...)) -> Response:
        user = self._auth_service.get_user_by_credentials(credentials.username, credentials.password)
        if not user:
            raise UnauthorizedException()

        access, refresh = self._auth_service.create_access_and_refresh_tokens(user)

        response = Response(data=AccessTokenOut(access_token=access))
        response.set_cookie(settings.REFRESH_TOKEN_COOKIE, refresh, httponly=True)

        return response

    def refresh(self, request: HttpRequest) -> Response:
        refresh_token: str = request.COOKIES.get(settings.REFRESH_TOKEN_COOKIE)
        if not refresh_token:
            raise UndefinedRefreshTokenException()

        payload = self._auth_service.try_get_payload(refresh_token)
        if not self._auth_service.is_payload_valid(payload):
            raise InvalidPayloadException()

        if not self._auth_service.is_token_alive(payload, TokenTypes.REFRESH, settings.REFRESH_TOKEN_TTL):
            raise AccessTokenTTLZeroException()

        token = self._auth_service.get_refresh_token_from_db(refresh_token)
        if not token:
            raise UnknownRefreshTokenException()

        tokens = self._auth_service.update_access_and_refresh_tokens(token)
        if not tokens:
            raise RevokedRefreshTokenException()

        access, refresh = tokens
        response = Response(data=AccessTokenOut(access_token=access))
        response.set_cookie(settings.REFRESH_TOKEN_COOKIE, refresh, httponly=True)

        return response
