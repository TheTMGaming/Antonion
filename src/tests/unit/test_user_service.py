from itertools import chain
from re import sub
from typing import List

import pytest
from telegram import User

from app.internal.models.bank import BankAccount, Transaction
from app.internal.models.user import TelegramUser
from app.internal.services.user import get_user, is_user_exist, try_add_or_update_user, try_set_phone

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
    was_added = try_add_or_update_user(user)
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

    was_added = try_add_or_update_user(user)
    assert not was_added

    _assert_telegram_user(user)


@pytest.mark.django_db
@pytest.mark.unit
def test_getting_user_by_identifier(users: List[User], telegram_users: List[TelegramUser]) -> None:
    assert all(telegram_users[i] == get_user(users[i].id) == get_user(users[i].username) for i in range(len(users)))


@pytest.mark.django_db
@pytest.mark.unit
def test_check_existing_of_user_by_id(users: List[User], telegram_users: List[TelegramUser]) -> None:
    assert all(is_user_exist(user.id) for user in users)


@pytest.mark.django_db
@pytest.mark.unit
@pytest.mark.parametrize("number", _CORRECTED_PHONE_NUMBERS + _WRONG_PHONE_NUMBERS)
def test_setting_phone(telegram_user: TelegramUser, number: str) -> None:
    expected = "+7" + sub("[^0-9]", "", number)[1:]

    was_set = try_set_phone(telegram_user.id, number)
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
