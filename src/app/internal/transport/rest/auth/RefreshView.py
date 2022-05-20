from django.conf import settings
from django.http import HttpRequest
from rest_framework.response import Response
from rest_framework.views import APIView

from app.internal.authentication.TokenTypes import TokenTypes
from app.internal.authentication.service import update_access_and_refresh_tokens, get_refresh_token_from_db
from app.internal.authentication.utils import try_get_payload, is_token_valid


class RefreshView(APIView):
    ACCESS_TOKEN = "access_token"

    NO_TOKEN_COOKIE = {"error": "Refresh token was not found in cookies"}
    TOKEN_WAS_BE_REVOKED = {"error": "Refresh token was be revoked"}
    INVALID_SIGNATURE_OR_TTL = {"error": "Invalid signature or ttl is zero"}
    UNKNOWN_TOKEN = {"error": "Unknown refresh token"}

    def post(self, request: HttpRequest) -> Response:
        refresh_token: str = request.COOKIES.get(settings.REFRESH_TOKEN_COOKIE)
        if not refresh_token:
            return Response(data=self.NO_TOKEN_COOKIE, status=400)

        if not is_token_valid(try_get_payload(refresh_token), TokenTypes.REFRESH, settings.REFRESH_TOKEN_TTL):
            return Response(data=self.INVALID_SIGNATURE_OR_TTL, status=400)

        token = get_refresh_token_from_db(refresh_token)
        if not token:
            return Response(data=self.UNKNOWN_TOKEN, status=400)

        tokens = update_access_and_refresh_tokens(token)
        if not tokens:
            return Response(data=self.TOKEN_WAS_BE_REVOKED, status=400)

        access, refresh = tokens
        response = Response(data={self.ACCESS_TOKEN: access})
        response.set_cookie(settings.REFRESH_TOKEN_COOKIE, refresh, httponly=True)

        return response
