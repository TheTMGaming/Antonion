from typing import Callable, Type

from django.http import HttpRequest, HttpResponse
from ninja import NinjaAPI

from app.internal.authentication.api import register_auth_api
from app.internal.bank.api import register_bank_api
from app.internal.exceptions import (
    AccessTokenTTLZeroException,
    APIException,
    BadRequestException,
    InvalidPayloadException,
    NotFoundException,
    UnauthorizedException,
    UndefinedRefreshTokenException,
    UnknownRefreshTokenException,
)
from app.internal.user.api import register_friends_api, register_user_api


def get_api() -> NinjaAPI:
    api = NinjaAPI(title="Банк мечты", description="Самый лучший банк из самых лучших банков")

    subscribe_exception_handlers(api)

    register_auth_api(api)
    register_user_api(api)
    register_friends_api(api)
    register_bank_api(api)

    return api


def subscribe_exception_handlers(api: NinjaAPI) -> None:
    exceptions = [
        UnauthorizedException,
        UndefinedRefreshTokenException,
        InvalidPayloadException,
        AccessTokenTTLZeroException,
        UnknownRefreshTokenException,
        BadRequestException,
        NotFoundException,
    ]

    for exception in exceptions:
        api.add_exception_handler(exception, get_exception_handler(api, exception))


def get_exception_handler(
    api: NinjaAPI, exception: Type[APIException]
) -> Callable[[HttpRequest, Exception], HttpResponse]:
    return lambda request, exc: exception.get_response(request, exc, api)
