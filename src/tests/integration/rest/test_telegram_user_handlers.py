import re

import pytest
from django.http import HttpRequest

from app.internal.general.rest.exceptions import BadRequestException
from app.internal.general.rest.responses import SuccessResponse
from app.internal.user.db.models import TelegramUser
from app.internal.user.db.repositories import SecretKeyRepository, TelegramUserRepository
from app.internal.user.domain.entities.user import PasswordIn, PhoneIn
from app.internal.user.domain.services import TelegramUserService
from app.internal.user.presentation.handlers import TelegramUserHandlers
from tests.conftest import KEY, PASSWORD, WRONG_KEY

user_service = TelegramUserService(user_repo=TelegramUserRepository(), secret_key_repo=SecretKeyRepository())
handlers = TelegramUserHandlers(user_service=user_service)


@pytest.mark.django_db
@pytest.mark.integration
def test_getting_about_me(http_request: HttpRequest) -> None:
    actual = handlers.get_about_me(http_request)
    expected = http_request.telegram_user

    assert actual.id == expected.id
    assert actual.phone == expected.phone
    assert actual.username == expected.username
    assert actual.first_name == expected.first_name
    assert actual.last_name == expected.last_name


@pytest.mark.django_db
@pytest.mark.integration
@pytest.mark.parametrize(
    ["phone", "is_error"],
    [
        ["88005553535", False],
        ["+78005553535", False],
        ["+88005553535", True],
        ["+38005553535", True],
        ["+38005553535", True],
        ["1337", True],
    ],
)
def test_updating_phone(http_request: HttpRequest, phone: str, is_error: bool) -> None:
    body = PhoneIn(phone=phone)

    if is_error:
        with pytest.raises(BadRequestException):
            handlers.update_phone(http_request, body)

        return

    actual = handlers.update_phone(http_request, body).phone

    assert actual.startswith("+7")
    assert actual[2:] == re.sub(r"\D", "", phone)[1:]


@pytest.mark.django_db
@pytest.mark.integration
def test_updating_password(http_request: HttpRequest, telegram_user_with_password: TelegramUser) -> None:
    assert handlers.update_password(http_request, PasswordIn(key=KEY, password=PASSWORD)) == SuccessResponse()

    with pytest.raises(BadRequestException):
        handlers.update_password(http_request, PasswordIn(key=WRONG_KEY, password=PASSWORD))
