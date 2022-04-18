from multiprocessing.connection import Client
from django.urls import reverse

import pytest
from django.conf import settings
from telegram import TelegramError

from app.internal.models.user import TelegramUser
from app.internal.transport.bot.webhook.BotWebhookService import BotWebhookService


@pytest.mark.django_db
def test_connection_with_db(telegram_user: TelegramUser) -> None:
    pass


def test_webhook_service() -> None:
    service = BotWebhookService(settings.TELEGRAM_BOT_TOKEN)

    try:
        service.handle({})
        assert True
    except TelegramError:
        assert False


@pytest.mark.django_db
def test_rest(telegram_user: TelegramUser, client: Client) -> None:
    url = reverse("me", args=[telegram_user.id])
    response = client.get(url)

    assert response.status_code == 200
