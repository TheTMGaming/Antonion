from abc import abstractmethod
from functools import partial

from django.http import HttpRequest, HttpResponse
from ninja import NinjaAPI


class APIException(Exception):
    @abstractmethod
    def handle(self, request: HttpRequest, exc, api: NinjaAPI) -> HttpResponse:
        pass


class BadRequestException(APIException):
    def handle(self, request: HttpRequest, exc, api: NinjaAPI) -> HttpResponse:
        return api.create_response(request, data={"error": "Check entered values or headers"}, status=400)


class IntegrityException(APIException):
    def handle(self, request: HttpRequest, exc, api: NinjaAPI) -> HttpResponse:
        return api.create_response(request, data={"error": "Database error"}, status=500)


class UnauthorizedException(APIException):
    def handle(self, request: HttpRequest, exc, api: NinjaAPI) -> HttpResponse:
        return api.create_response(request, data={"error": "Unauthorized"}, status=401)


class UndefinedRefreshTokenException(APIException):
    def handle(self, request: HttpRequest, exc, api: NinjaAPI) -> HttpResponse:
        return api.create_response(request, data={"error": "Refresh token is undefined"}, status=400)


class InvalidPayloadException(APIException):
    def handle(self, request: HttpRequest, exc, api: NinjaAPI) -> HttpResponse:
        return api.create_response(request, data={"error": "Access token's payload is invalid"}, status=400)


class AccessTokenTTLZeroException(APIException):
    def handle(self, request: HttpRequest, exc, api: NinjaAPI) -> HttpResponse:
        return api.create_response(request, data={"error": "TTL is zero"}, status=400)


class UnknownRefreshTokenException(APIException):
    def handle(self, request: HttpRequest, exc, api: NinjaAPI) -> HttpResponse:
        return api.create_response(request, data={"error": "Unknown refresh token"}, status=400)


class RevokedRefreshTokenException(APIException):
    def handle(self, request: HttpRequest, exc, api: NinjaAPI) -> HttpResponse:
        return api.create_response(request, data={"error": "Refresh token was be revoked"}, status=400)


def add_exceptions(api: NinjaAPI) -> None:
    exceptions = {
        UnauthorizedException,
        UndefinedRefreshTokenException,
        InvalidPayloadException,
        AccessTokenTTLZeroException,
        UnknownRefreshTokenException,
        BadRequestException,
    }

    for exception in exceptions:
        api.add_exception_handler(exception, partial(exception().handle, api=api))
