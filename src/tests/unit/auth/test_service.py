from datetime import datetime

import pytest
from freezegun import freeze_time

from app.internal.authentication.domain.services.TokenTypes import TokenTypes
from app.internal.authentication.service import (
    create_access_and_refresh_tokens,
    get_user_by_credentials,
    update_access_and_refresh_tokens,
)
from app.internal.authentication.utils import CREATED_AT, TELEGRAM_ID, TOKEN_TYPE, try_get_payload
from app.internal.models.user import RefreshToken, TelegramUser
from tests.conftest import PASSWORD


@pytest.mark.django_db
@pytest.mark.unit
def test_getting_user_by_credentials(telegram_user_with_password: TelegramUser) -> None:
    username = telegram_user_with_password.username

    correct = get_user_by_credentials(username, PASSWORD)
    wrong = get_user_by_credentials(PASSWORD, username)

    assert correct == telegram_user_with_password
    assert wrong is None


@freeze_time("2022-05-21")
@pytest.mark.django_db
@pytest.mark.unit
def test_creating_tokens(telegram_user: TelegramUser) -> None:
    access, refresh = create_access_and_refresh_tokens(telegram_user)
    actual_refresh_tokens = RefreshToken.objects.filter(telegram_user=telegram_user).all()

    _assert_tokens(access, refresh, telegram_user)
    assert len(actual_refresh_tokens) == 1
    assert actual_refresh_tokens[0].value == refresh


@freeze_time("2022-05-21")
@pytest.mark.django_db
@pytest.mark.unit
def test_updating_tokens(telegram_user: TelegramUser, refresh_token: RefreshToken) -> None:
    tokens = update_access_and_refresh_tokens(refresh_token)

    assert tokens is not None
    _assert_tokens(tokens[0], tokens[1], telegram_user)
    assert RefreshToken.objects.filter(pk=refresh_token.pk).first().revoked
    assert RefreshToken.objects.filter(telegram_user=telegram_user, revoked=False).count() > 0


@freeze_time("2022-05-21")
@pytest.mark.django_db
@pytest.mark.unit
def test_updating_tokens__revoking_all(telegram_user: TelegramUser, refresh_token: RefreshToken) -> None:
    refresh_token.revoked = True
    refresh_token.save(update_fields=["revoked"])

    tokens = update_access_and_refresh_tokens(refresh_token)

    assert tokens is None
    assert RefreshToken.objects.filter(telegram_user=telegram_user, revoked=False).count() == 0


def _assert_tokens(access: str, refresh: str, telegram_user: TelegramUser) -> None:
    access_payload, refresh_payload = try_get_payload(access), try_get_payload(refresh)

    payload = {TELEGRAM_ID: telegram_user.id, CREATED_AT: datetime.now().timestamp()}
    assert access_payload == payload | {TOKEN_TYPE: TokenTypes.ACCESS.value}
    assert refresh_payload == payload | {TOKEN_TYPE: TokenTypes.REFRESH.value}
