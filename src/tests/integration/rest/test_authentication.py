from datetime import datetime
from unittest.mock import MagicMock

import freezegun
import jwt
import pytest
from django.conf import settings
from django.http import HttpRequest
from ninja.security import HttpBearer

from app.internal.authentication.db.repositories import AuthRepository
from app.internal.authentication.domain.services import JWTService
from app.internal.authentication.domain.services.TokenTypes import TokenTypes
from app.internal.authentication.presentation import JWTAuthentication
from app.internal.user.db.models import TelegramUser
from app.internal.user.db.repositories import TelegramUserRepository

service = JWTService(auth_repo=AuthRepository(), user_repo=TelegramUserRepository())


@freezegun.freeze_time("2022-05-21")
@pytest.mark.django_db
@pytest.mark.integration
def test_ok(http_request: HttpRequest, telegram_user: TelegramUser) -> None:
    token = service.generate_token(telegram_user.id, TokenTypes.ACCESS)
    http_request.headers[HttpBearer.header] = f"Bearer {token}"

    JWTAuthentication()(http_request)

    assert hasattr(http_request, "telegram_user")
    assert http_request.telegram_user == telegram_user


@freezegun.freeze_time("2022-05-21")
@pytest.mark.django_db
@pytest.mark.integration
def test_wrong_payload(http_request: HttpRequest) -> None:
    token = jwt.encode({"stupid": 1337}, settings.SECRET_KEY)
    http_request.headers[HttpBearer.header] = f"Bearer {token}"

    assert_error(http_request)


@freezegun.freeze_time("2022-05-21")
@pytest.mark.django_db
@pytest.mark.integration
def test_dead_token(http_request: HttpRequest) -> None:
    now = datetime.now()

    token = jwt.encode(
        {service.TELEGRAM_ID: 123, service.TOKEN_TYPE: 123, service.CREATED_AT: now.timestamp()}, settings.SECRET_KEY
    )
    http_request.headers[HttpBearer.header] = f"Bearer {token}"

    freezegun.api.freeze_time(now - 2 * settings.ACCESS_TOKEN_TTL)
    assert_error(http_request)


def assert_error(http_request: HttpRequest) -> None:
    JWTAuthentication()(http_request)

    assert hasattr(http_request, "telegram_user") and http_request.telegram_user is None
