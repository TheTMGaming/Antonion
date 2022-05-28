from typing import Type

from ninja import NinjaAPI

from .auth import (
    AccessTokenTTLZeroException,
    AccessTokenTTLZeroResponse,
    InvalidPayloadException,
    InvalidPayloadResponse,
    UnauthorizedException,
    UnauthorizedResponse,
    UndefinedRefreshTokenException,
    UndefinedRefreshTokenResponse,
    UnknownRefreshTokenException,
    UnknownRefreshTokenResponse,
)
from .ErrorResponse import ErrorResponse


def register_exceptions(api: NinjaAPI) -> None:
    responses = {
        UnauthorizedException: UnauthorizedResponse,
        UndefinedRefreshTokenException: UndefinedRefreshTokenResponse,
        InvalidPayloadException: InvalidPayloadResponse,
        AccessTokenTTLZeroException: AccessTokenTTLZeroResponse,
        UnknownRefreshTokenException: UnknownRefreshTokenResponse,
    }

    for exception, response in responses.items():
        api.add_exception_handler(exception, lambda request, exc: response.create(api, request, exc))
