import random
import string
from itertools import chain
from re import sub
from typing import List

import pytest
from telegram import User

from app.internal.general.services import user_service
from app.internal.user.db.models import SecretKey, TelegramUser
from tests.conftest import KEY, TIP, WRONG_KEY

chars = string.printable

_CORRECTED_PHONE_NUMBERS = list(
    chain(
        *(
            [
                f"{start}8005553535",
                f"{start} (800) 555 35 35",
                f"{start}-(800)-555-35-35",
                f"{start}-800-555-35-35",
                f"{start}800 55 535 35",
                f"{start}.800.55,535,35",
            ]
            for start in ["7", "8", "+7"]
        )
    )
)

_WRONG_PHONE_NUMBERS = [
    *(f"+{start}8005553535" for start in chain(range(7), [8, 9])),
    *(f"{start}8005553535" for start in chain(range(7), [9])),
    *("1" * length for length in chain(range(11), range(12, 30))),
    *("a" * length for length in chain(range(11), range(12, 30))),
    *("a1" * (length // 2) + "a" * (length % 2) for length in range(30)),
    *("8" * 11 + "a" * amount for amount in range(1, 6)),
    *("8" * 11 + " " + "a" * amount for amount in range(1, 6)),
    *("8" * 11 + " " * amount for amount in range(1, 6)),
    *(" " * amount for amount in range(30)),
    "",
]


@pytest.mark.django_db
@pytest.mark.unit
def test_adding_user_to_db(user: User) -> None:
    was_added = user_service.try_add_or_update_user(user)
    assert was_added

    _assert_telegram_user(user)


@pytest.mark.django_db
@pytest.mark.unit
def test_updating_user_in_db(telegram_user: TelegramUser) -> None:
    user = User(
        id=telegram_user.id,
        first_name=telegram_user.first_name[::-1],
        last_name=telegram_user.last_name[::-1],
        username=telegram_user.username[::-1],
        is_bot=False,
    )

    was_added = user_service.try_add_or_update_user(user)
    assert not was_added

    _assert_telegram_user(user)


@pytest.mark.django_db
@pytest.mark.unit
def test_getting_user_by_identifier(users: List[User], telegram_users: List[TelegramUser]) -> None:
    assert all(
        telegram_users[i] == user_service.get_user(users[i].id) == user_service.get_user(users[i].username)
        for i in range(len(users))
    )


@pytest.mark.django_db
@pytest.mark.unit
@pytest.mark.parametrize("number", _CORRECTED_PHONE_NUMBERS + _WRONG_PHONE_NUMBERS)
def test_setting_phone(telegram_user: TelegramUser, number: str) -> None:
    expected = "+7" + sub(r"\D", "", number)[1:]

    was_set = user_service.try_set_phone(telegram_user.id, number)
    user = TelegramUser.objects.filter(id=telegram_user.id).first()

    assert was_set and user.phone == expected or not was_set and user.phone is None


def _assert_telegram_user(expected: User) -> None:
    actual = TelegramUser.objects.filter(id=expected.id).all()

    assert actual is not None
    assert actual.count() == 1
    assert actual[0].username == expected.username
    assert actual[0].first_name == expected.first_name
    assert actual[0].last_name == expected.last_name
    assert actual[0].phone is None


@pytest.mark.django_db
@pytest.mark.unit
def test_updating_password(user: User, telegram_user_with_password: TelegramUser) -> None:
    was = telegram_user_with_password.password
    is_updated = user_service.try_update_password(user, "".join(random.choice(chars) for _ in range(5)))

    actual = TelegramUser.objects.filter(pk=telegram_user_with_password.pk).first()

    assert is_updated
    assert actual.password != was


@pytest.mark.django_db
@pytest.mark.unit
def test_creating_password(user: User, telegram_user: TelegramUser) -> None:
    password = "a" * 5

    is_created = user_service.try_create_password(user, password, KEY, TIP)

    assert is_created
    assert TelegramUser.objects.filter(pk=telegram_user.pk).first().password is not None
    assert SecretKey.objects.filter(telegram_user=telegram_user).exists()


@pytest.mark.django_db
@pytest.mark.unit
def test_confirmation_secret_key(user: User, telegram_user_with_password: TelegramUser) -> None:
    assert user_service.is_secret_key_correct(user, KEY) is True
    assert user_service.is_secret_key_correct(user, WRONG_KEY) is False
