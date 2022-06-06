from abc import abstractmethod
from functools import partial

from django.http import HttpRequest, HttpResponse
from ninja import NinjaAPI


class APIException(Exception):
    @classmethod
    @abstractmethod
    def get_response(cls, request: HttpRequest, exc, api: NinjaAPI) -> HttpResponse:
        pass


class BadRequestException(APIException):
    def __init__(self, message: str = "Check entered values or headers"):
        self.message = message

    @classmethod
    def get_response(cls, request: HttpRequest, exc, api: NinjaAPI) -> HttpResponse:
        return api.create_response(request, data={"error": exc.message}, status=400)


class IntegrityException(APIException):
    @classmethod
    def get_response(cls, request: HttpRequest, exc, api: NinjaAPI) -> HttpResponse:
        return api.create_response(request, data={"error": "Database error"}, status=500)


class UnauthorizedException(APIException):
    @classmethod
    def get_response(cls, request: HttpRequest, exc, api: NinjaAPI) -> HttpResponse:
        return api.create_response(request, data={"error": "Unauthorized"}, status=401)


class UndefinedRefreshTokenException(APIException):
    @classmethod
    def get_response(cls, request: HttpRequest, exc, api: NinjaAPI) -> HttpResponse:
        return api.create_response(request, data={"error": "Refresh token is undefined"}, status=400)


class InvalidPayloadException(APIException):
    @classmethod
    def get_response(cls, request: HttpRequest, exc, api: NinjaAPI) -> HttpResponse:
        return api.create_response(request, data={"error": "Access token's payload is invalid"}, status=400)


class AccessTokenTTLZeroException(APIException):
    @classmethod
    def get_response(cls, request: HttpRequest, exc, api: NinjaAPI) -> HttpResponse:
        return api.create_response(request, data={"error": "TTL is zero"}, status=400)


class UnknownRefreshTokenException(APIException):
    @classmethod
    def get_response(cls, request: HttpRequest, exc, api: NinjaAPI) -> HttpResponse:
        return api.create_response(request, data={"error": "Unknown refresh token"}, status=400)


class RevokedRefreshTokenException(APIException):
    @classmethod
    def get_response(cls, request: HttpRequest, exc, api: NinjaAPI) -> HttpResponse:
        return api.create_response(request, data={"error": "Refresh token was be revoked"}, status=400)


class NotFoundException(APIException):
    def __init__(self, what: str = "resource"):
        self.what = what

    @classmethod
    def get_response(cls, request: HttpRequest, exc, api: NinjaAPI) -> HttpResponse:
        return api.create_response(request, data={"error": f"Not found: {exc.what}"}, status=404)
