from json import loads

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.views import View

from app.internal.transport.bot.webhook.BotWebhookService import BotWebhookService


class BotWebhook(View):
    _service = BotWebhookService(settings.TELEGRAM_BOT_TOKEN)

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        json = loads(request.body)
        self._service.handle(json)

        return HttpResponse(status=200)
