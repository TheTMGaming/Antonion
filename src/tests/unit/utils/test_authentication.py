from datetime import datetime, timedelta

import pytest
from django.conf import settings
from freezegun import freeze_time

from app.internal.authentication.TokenTypes import TokenTypes
from app.internal.authentication.utils import (
    CREATED_AT,
    TELEGRAM_ID,
    TOKEN_TYPE,
    generate_token,
    is_token_valid,
    now,
    try_get_payload,
)


@pytest.mark.unit
def test_getting_payload() -> None:
    expected = {TELEGRAM_ID: 123, CREATED_AT: datetime.now().timestamp(), TOKEN_TYPE: TokenTypes.ACCESS}

    token = generate_token(expected[TELEGRAM_ID], expected[TOKEN_TYPE])

    actual = try_get_payload(token)

    assert actual == expected


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
def test_is_access_token_alive(delta: timedelta, is_alive: bool) -> None:
    payload = {CREATED_AT: (now() + delta).timestamp()}

    assert is_token_valid(payload) == is_alive
