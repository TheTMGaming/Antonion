from typing import List, Tuple

import pytest
from telegram import User

from app.internal.models.user import TelegramUser
from app.internal.services.friend import add_friend, get_friend, get_friends, is_friend_exist


@pytest.mark.django_db
def test_adding_friend(telegram_user: TelegramUser, friends: List[TelegramUser]) -> None:
    _add_friend(telegram_user, friends)

    assert friends == list(telegram_user.friends.all())


@pytest.mark.django_db
def test_getting_friend_by_identifier(telegram_user: TelegramUser, friends: List[TelegramUser]) -> None:
    _add_friend(telegram_user, friends)

    actual_by_id = [get_friend(telegram_user, friend.id) for friend in friends]
    actual_by_username = [get_friend(telegram_user, friend.username) for friend in friends]

    assert friends == actual_by_id == actual_by_username


@pytest.mark.django_db
def test_getting_friends(telegram_user: TelegramUser, friends: List[TelegramUser]) -> None:
    _add_friend(telegram_user, friends)

    actual = get_friends(telegram_user)

    assert list(actual) == list(telegram_user.friends.all())


@pytest.mark.django_db
def test_check_friend_exist(telegram_user: TelegramUser, friends: List[TelegramUser]) -> None:
    _add_friend(telegram_user, friends)

    assert all(is_friend_exist(telegram_user, friend) for friend in friends)


def _add_friend(user: TelegramUser, friends: List[TelegramUser]) -> None:
    [add_friend(user, friend) for friend in friends]
