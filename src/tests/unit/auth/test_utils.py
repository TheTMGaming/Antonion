from datetime import timedelta
from typing import Any, Dict
from unittest.mock import Mock

import pytest
from django.conf import settings
from freezegun import freeze_time

from app.internal.authentication import IsAuthenticated
from app.internal.authentication.domain.services.TokenTypes import TokenTypes
from app.internal.authentication.utils import (
    CREATED_AT,
    TELEGRAM_ID,
    TOKEN_TYPE,
    TelegramUser,
    generate_token,
    get_authenticated_telegram_user,
    is_payload_valid,
    is_token_alive,
    now,
    try_get_payload,
)


@pytest.mark.unit
def test_getting_payload(token_type=TokenTypes.ACCESS) -> None:
    expected = {TELEGRAM_ID: 123, CREATED_AT: now().timestamp(), TOKEN_TYPE: token_type.value}

    token = generate_token(expected[TELEGRAM_ID], token_type)

    actual = try_get_payload(token)

    assert actual == expected


@pytest.mark.unit
def test_getting_bad_payload() -> None:
    token = "imstupidtoken"
    payload = try_get_payload(token)

    assert payload == {}


@pytest.mark.django_db
@pytest.mark.unit
def test_getting_authenticated_user(telegram_user: TelegramUser) -> None:
    payload = {TELEGRAM_ID: telegram_user.id}
    actual = get_authenticated_telegram_user(payload)

    assert actual == telegram_user


@pytest.mark.django_db
@pytest.mark.unit
def test_getting_authenticated_user() -> None:
    payload = {TELEGRAM_ID: 1337}
    actual = get_authenticated_telegram_user(payload)

    assert actual is None


@pytest.mark.unit
@pytest.mark.parametrize(
    ["payload", "is_valid"],
    [
        [{}, False],
        [None, False],
        [{CREATED_AT: 123}, False],
        [{CREATED_AT: 123, TELEGRAM_ID: 123}, False],
        [{CREATED_AT: 123, TELEGRAM_ID: 123, TOKEN_TYPE: "dude"}, True],
        [{CREATED_AT: 123, TELEGRAM_ID: 123, TOKEN_TYPE: "dude", "opa": 123}, False],
        [{CREATED_AT: 123, TELEGRAM_ID: 123, TOKEN_TYPE: "dude", "opa": 123, "ta": 123}, False],
    ],
)
def test_validation_payload(payload: Dict[str, Any], is_valid: bool) -> None:
    assert is_payload_valid(payload) == is_valid


@freeze_time(now())
@pytest.mark.parametrize(
    ["delta", "is_alive"],
    [
        [-settings.ACCESS_TOKEN_TTL, False],
        [-settings.ACCESS_TOKEN_TTL - timedelta(seconds=1), False],
        [-settings.ACCESS_TOKEN_TTL - timedelta(milliseconds=1), False],
        [-2 * settings.ACCESS_TOKEN_TTL, False],
        [timedelta(milliseconds=0), True],
        [-settings.ACCESS_TOKEN_TTL + timedelta(seconds=1), True],
        [-settings.ACCESS_TOKEN_TTL + timedelta(milliseconds=1), True],
        [-timedelta(seconds=1), True],
        [-timedelta(milliseconds=1), True],
    ],
)
def test_is_token_alive(delta: timedelta, is_alive: bool) -> None:
    payload = {TELEGRAM_ID: 123, TOKEN_TYPE: TokenTypes.ACCESS.value, CREATED_AT: (now() + delta).timestamp()}

    assert is_token_alive(payload, TokenTypes.ACCESS, settings.ACCESS_TOKEN_TTL) == is_alive


@pytest.mark.unit
def test_authenticated_permission__no_attribute() -> None:
    assert not IsAuthenticated().has_permission(Mock([]), None)


@pytest.mark.unit
def test_authenticated_permission__attribute_is_none() -> None:
    request = Mock(["telegram_user"])
    request.telegram_user = None

    assert not IsAuthenticated().has_permission(request, None)


@pytest.mark.django_db
@pytest.mark.unit
def test_authenticated_permission(telegram_user: TelegramUser) -> None:
    request = Mock(["telegram_user"])
    request.telegram_user = telegram_user

    assert IsAuthenticated().has_permission(request, None)
