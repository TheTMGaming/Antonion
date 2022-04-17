from itertools import chain
from re import sub
from typing import Dict, List

import pytest
from telegram import User

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
def test_adding_user_to_db(first_user: User) -> None:
    was_added = try_add_or_update_user(first_user)
    assert was_added

    _assert_telegram_user(first_user)


@pytest.mark.django_db
def test_updating_user_in_db(first_user: User, second_user: User) -> None:
    _create_telegram_user(first_user)

    first_user.username = second_user.username
    first_user.first_name = second_user.first_name
    first_user.last_name = second_user.last_name

    was_added = try_add_or_update_user(first_user)
    assert not was_added

    _assert_telegram_user(first_user)


@pytest.mark.django_db
def test_getting_user_by_identifier(users: List[User]) -> None:
    telegram_users = _create_dict_of_added_users(users)

    assert all(
        telegram_user == get_user(user.id) == get_user(user.username) for user, telegram_user in telegram_users.items()
    )


@pytest.mark.django_db
def test_check_existing_of_user_by_id(users: List[User]) -> None:
    [_create_telegram_user(user) for user in users]

    assert all(is_user_exist(user.id) for user in users)


@pytest.mark.django_db
@pytest.mark.parametrize("number", _CORRECTED_PHONE_NUMBERS + _WRONG_PHONE_NUMBERS)
def test_setting_phone(first_user: User, number: str) -> None:
    _create_telegram_user(first_user)
    expected = "+7" + sub("[^0-9]", "", number)[1:]

    was_set = try_set_phone(first_user.id, number)
    user = TelegramUser.objects.filter(id=first_user.id).first()

    assert was_set and user.phone == expected or not was_set and user.phone is None


def _create_dict_of_added_users(users: List[User]) -> Dict[User, TelegramUser]:
    return dict((user, _create_telegram_user(user)) for user in users)


def _create_telegram_user(user: User) -> TelegramUser:
    return TelegramUser.objects.create(
        id=user.id, username=user.username, first_name=user.first_name, last_name=user.last_name
    )


def _assert_telegram_user(expected: User) -> None:
    actual = TelegramUser.objects.filter(id=expected.id).all()

    assert actual is not None
    assert actual.count() == 1
    assert actual[0].username == expected.username
    assert actual[0].first_name == expected.first_name
    assert actual[0].last_name == expected.last_name
    assert actual[0].phone is None
