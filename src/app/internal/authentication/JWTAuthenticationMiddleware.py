from django.conf import settings
from django.http import HttpRequest, HttpResponse, JsonResponse

from app.internal.authentication.TokenTypes import TokenTypes
from app.internal.authentication.utils import (
    get_authenticated_telegram_user,
    is_token_valid,
    try_get_payload,
)


class JWTAuthenticationMiddleware:
    API = "/api"
    HEADER = "Authorization"
    BEARER = "bearer"

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        parameters = request.headers.get(self.HEADER, "").split()

        if len(parameters) < 2 or parameters[0].lower() != self.BEARER:
            return self.get_response(request)

        bearer, token = parameters
        payload = try_get_payload(token)
        if payload is not None and is_token_valid(payload, TokenTypes.ACCESS, settings.ACCESS_TOKEN_TTL):
            request.telegram_user = get_authenticated_telegram_user(payload)

        return self.get_response(request)
