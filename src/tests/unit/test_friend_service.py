from typing import List

import pytest

from app.internal.general.services import friend_service
from app.internal.user.db.models import TelegramUser


@pytest.mark.django_db
@pytest.mark.unit
def test_getting_friend(telegram_user: TelegramUser, friends: List[TelegramUser]) -> None:
    actual_by_id = [friend_service.get_friend(telegram_user, friend.id) for friend in friends]
    actual_by_username = [friend_service.get_friend(telegram_user, friend.username) for friend in friends]

    assert friends == actual_by_id == actual_by_username


@pytest.mark.django_db
@pytest.mark.unit
def test_getting_friends(telegram_user: TelegramUser, friends: List[TelegramUser]) -> None:
    friends = sorted(friends, key=lambda friend: friend.id)
    actual = sorted(friend_service.get_friends(telegram_user), key=lambda friend: friend.id)

    assert actual == friends


@pytest.mark.django_db
@pytest.mark.unit
def test_getting_friends_as_dict(telegram_user: TelegramUser, friends: List[TelegramUser]) -> None:
    actual = friend_service.get_friends_as_dict(telegram_user)

    assert sorted(actual.keys()) == list(range(1, len(friends) + 1))
    assert sorted(actual.values(), key=lambda user: user.id) == sorted(friends, key=lambda user: user.id)


@pytest.mark.django_db
@pytest.mark.unit
def test_removing_friend(telegram_user: TelegramUser, friend: TelegramUser) -> None:
    friend_service.remove_from_friends(telegram_user, friend)
    assert not telegram_user.friends.filter(id=friend.id).exists()


@pytest.mark.django_db
@pytest.mark.unit
def test_checking_friend_exist(telegram_user: TelegramUser, friends: List[TelegramUser]) -> None:
    assert all(friend_service.is_friend_exists(telegram_user, friend) for friend in friends)
