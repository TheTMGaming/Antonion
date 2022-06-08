from multiprocessing.connection import Client

import freezegun
import pytest
from django.conf import settings
from django.urls import reverse
from telegram import TelegramError

from app.internal.authentication.db.repositories import AuthRepository
from app.internal.authentication.domain.services import JWTService
from app.internal.authentication.domain.services.TokenTypes import TokenTypes
from app.internal.user.db.models import TelegramUser
from app.internal.user.db.repositories import TelegramUserRepository
from app.internal.webhook.BotWebhookService import BotWebhookService


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


@freezegun.freeze_time("2022-06-02")
@pytest.mark.django_db
@pytest.mark.smoke
def test_rest(telegram_user_with_phone: TelegramUser, client: Client) -> None:
    service = JWTService(auth_repo=AuthRepository(), user_repo=TelegramUserRepository())

    url = reverse("api-1.0.0:me")

    headers = {"HTTP_AUTHORIZATION": f"Bearer {service.generate_token(telegram_user_with_phone.id, TokenTypes.ACCESS)}"}
    response = client.get(url, **headers)

    assert response.status_code == 200
