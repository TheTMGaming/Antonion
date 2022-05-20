import random
import string

import pytest
from telegram import User

from app.internal.models.user import SecretKey, TelegramUser
from app.internal.services.user import is_secret_key_correct, try_create_password, try_update_password
from tests.conftest import KEY, TIP, WRONG_KEY

chars = string.printable


@pytest.mark.django_db
@pytest.mark.unit
def test_updating_password(user: User, telegram_user_with_password: TelegramUser) -> None:
    was = telegram_user_with_password.password
    is_updated = try_update_password(user, "".join(random.choice(chars) for _ in range(5)))

    actual = TelegramUser.objects.filter(pk=telegram_user_with_password.pk).first()

    assert is_updated
    assert actual.password != was


@pytest.mark.django_db
@pytest.mark.unit
def test_creating_password(user: User, telegram_user: TelegramUser) -> None:
    password = "a" * 5

    is_created = try_create_password(user, password, KEY, TIP)

    assert is_created
    assert TelegramUser.objects.filter(pk=telegram_user.pk).first().password is not None
    assert SecretKey.objects.filter(telegram_user=telegram_user).exists()


@pytest.mark.django_db
@pytest.mark.unit
def test_confirmation_secret_key(user: User, telegram_user_with_password: TelegramUser) -> None:
    assert is_secret_key_correct(KEY, user) is True
    assert is_secret_key_correct(WRONG_KEY, user) is False
