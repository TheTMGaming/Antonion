from django.conf import settings
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from app.internal.authentication.service import create_access_and_refresh_tokens, get_user_by_credentials


class LoginView(APIView):
    USERNAME = "username"
    PASSWORD = "password"
    ACCESS_TOKEN = "access_token"

    CREDENTIALS_ERROR = {"error": "Expected username and password"}

    def post(self, request: Request) -> Response:
        username, password = request.data.get(self.USERNAME), request.data.get(self.PASSWORD)

        if not all([username, password]):
            return Response(data=self.CREDENTIALS_ERROR, status=400)

        user = get_user_by_credentials(username, password)
        if not user:
            return Response(status=401)

        access, refresh = create_access_and_refresh_tokens(user)

        response = Response(data={self.ACCESS_TOKEN: access})
        response.set_cookie(settings.REFRESH_TOKEN_COOKIE, refresh, httponly=True)

        return response
