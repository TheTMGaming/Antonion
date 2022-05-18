from datetime import datetime, timedelta

from django.apps import apps
from django.conf import settings
from django.http import HttpRequest, HttpResponse, JsonResponse
from jwt import PyJWTError, decode

TelegramUser = apps.get_model("app", "TelegramUser", require_ready=True)


class JWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        if not request.path.startswith("/api"):
            return self.get_response(request)

        try:
            token = request.headers.get("authorization")
            payload = decode(token, settings.SECRET_KEY, algorithms=["HS256"])

            request.telegram_user = TelegramUser.objects.filter(id=payload["telegram_id"]).first()

            lifetime = datetime.now(tz=settings.TIME_ZONE) - payload["created_at"]
            ttl = settings.ACCESS_TOKEN_TTL - lifetime

            if not request.telegram_user:
                return JsonResponse(data={"error": "Unknown telegram_id"}, status=401)

            if ttl <= timedelta(seconds=0):
                return JsonResponse(data={"error": "TTL is zero"}, status=401)

            return self.get_response(request)

        except PyJWTError:
            return HttpResponse(status=401)
