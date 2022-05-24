from datetime import datetime
from typing import Any, Dict
from unittest.mock import MagicMock

import freezegun
import jwt
import pytest
from django.conf import settings

from app.internal.authentication.domain.services.TokenTypes import TokenTypes
from app.internal.authentication.presentation import JWTAuthentication
from app.internal.authentication.utils import CREATED_AT, TELEGRAM_ID, TOKEN_TYPE, generate_token
from app.internal.models.user import TelegramUser


@pytest.mark.django_db
@pytest.mark.integration
@pytest.mark.parametrize(
    ["headers", "token"],
    [
        [{}, None],
        [{"header": "stupid"}, None],
        [{JWTAuthentication.TOKEN_HEADER: "123"}, None],
        [{JWTAuthentication.TOKEN_HEADER: "123 123"}, None],
        [{JWTAuthentication.TOKEN_HEADER: "123 123 123"}, None],
        [{JWTAuthentication.TOKEN_HEADER: "bearer123"}, None],
        [{JWTAuthentication.TOKEN_HEADER: "bearer 123 123"}, None],
        [{JWTAuthentication.TOKEN_HEADER: "bearer 123"}, "123"],
        [{JWTAuthentication.TOKEN_HEADER: "bearer 123 "}, "123"],
        [{JWTAuthentication.TOKEN_HEADER: "bearer   123 "}, "123"],
        [{JWTAuthentication.TOKEN_HEADER: "bearer   123   "}, "123"],
        [{JWTAuthentication.TOKEN_HEADER: "Bearer 123"}, "123"],
        [{JWTAuthentication.TOKEN_HEADER: "BEARER 123"}, "123"],
        [{JWTAuthentication.TOKEN_HEADER: "BeArER 123"}, "123"],
    ],
)
def test_getting_bearer_token(
    headers: Dict[str, Any], token: str, http_request: MagicMock, get_response: MagicMock
) -> None:
    http_request.headers = headers

    middleware = JWTAuthentication(get_response)

    assert middleware._get_bearer_token(http_request) == token


@freezegun.freeze_time("2022-05-21")
@pytest.mark.django_db
@pytest.mark.integration
def test_authentication_user__ok(http_request: MagicMock, get_response: MagicMock, telegram_user: TelegramUser) -> None:
    token = generate_token(telegram_user.id, TokenTypes.ACCESS)
    http_request.headers[JWTAuthentication.TOKEN_HEADER] = f"Bearer {token}"

    JWTAuthentication(get_response)(http_request)

    assert hasattr(http_request, "telegram_user")
    assert http_request.telegram_user == telegram_user
    get_response.assert_called_once()


@freezegun.freeze_time("2022-05-21")
@pytest.mark.integration
def test_authentication_user__wrong_payload(http_request: MagicMock, get_response: MagicMock) -> None:
    token = jwt.encode({"stupid": 1337}, settings.SECRET_KEY)
    http_request.headers[JWTAuthentication.TOKEN_HEADER] = f"Bearer {token}"

    _assert_error(http_request, get_response)


@freezegun.freeze_time("2022-05-21")
@pytest.mark.integration
def test_authentication_user__dead_token(http_request: MagicMock, get_response: MagicMock) -> None:
    now = datetime.now()

    token = jwt.encode({TELEGRAM_ID: 123, TOKEN_TYPE: 123, CREATED_AT: now.timestamp()}, settings.SECRET_KEY)
    http_request.headers[JWTAuthentication.TOKEN_HEADER] = f"Bearer {token}"

    freezegun.api.freeze_time(now - 2 * settings.ACCESS_TOKEN_TTL)
    _assert_error(http_request, get_response)


def _assert_error(http_request: MagicMock, get_response: MagicMock) -> None:
    JWTAuthentication(get_response)(http_request)

    assert hasattr(http_request, "telegram_user")
    assert http_request.telegram_user is None
    get_response.assert_called_once()
