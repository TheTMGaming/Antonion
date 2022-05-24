from multiprocessing.connection import Client

import pytest
from django.conf import settings
from django.urls import reverse
from telegram import TelegramError

from app.internal.bot.webhook.BotWebhookService import BotWebhookService
from app.internal.users.db.models import TelegramUser


@pytest.mark.django_db
@pytest.mark.smoke
def test_connection_with_db(telegram_user: TelegramUser) -> None:
    pass


@pytest.mark.smoke
def test_webhook_service() -> None:
    service = BotWebhookService(settings.TELEGRAM_BOT_TOKEN)

    try:
        service.handle({})
        assert True
    except TelegramError:
        assert False


@pytest.mark.django_db
@pytest.mark.smoke
def test_rest(telegram_user: TelegramUser, client: Client) -> None:
    url = reverse("me", args=[telegram_user.id])
    response = client.get(url)

    assert response.status_code == 200
