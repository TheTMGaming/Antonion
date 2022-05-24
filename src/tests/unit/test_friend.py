from typing import List

import pytest

from app.internal.users.db.models import FriendRequest, TelegramUser
from app.internal.users.db.repositories import FriendRequestRepository, TelegramUserRepository
from app.internal.users.domain.services import FriendService

user_repo = TelegramUserRepository()
request_repo = FriendRequestRepository()
friend_service = FriendService(friend_repo=user_repo, request_repo=request_repo)


@pytest.mark.django_db
@pytest.mark.unit
def test_getting_friend(telegram_user: TelegramUser, friends: List[TelegramUser]) -> None:
    actual_by_id = [user_repo.get_friend(telegram_user, friend.id) for friend in friends]
    actual_by_username = [user_repo.get_friend(telegram_user, friend.username) for friend in friends]

    assert friends == actual_by_id == actual_by_username


@pytest.mark.django_db
@pytest.mark.unit
def test_checking_friend_exist(telegram_user: TelegramUser, friends: List[TelegramUser]) -> None:
    assert all(user_repo.is_friend_exists(telegram_user, friend) for friend in friends)


@pytest.mark.django_db
@pytest.mark.unit
def test_creating_friend_request(telegram_user: TelegramUser, another_telegram_user: TelegramUser) -> None:
    is_created = friend_service.try_create_friend_request(another_telegram_user, telegram_user)
    requests = FriendRequest.objects.filter(source=another_telegram_user, destination=telegram_user).all()

    assert is_created
    assert requests is not None
    assert len(requests) == 1
    assert requests[0].source == another_telegram_user and requests[0].destination == telegram_user


@pytest.mark.django_db
@pytest.mark.unit
def test_creating_friend_request__already_exist(
    telegram_user: TelegramUser, another_telegram_user: TelegramUser, friend_request: FriendRequest
) -> None:
    is_created = friend_service.try_create_friend_request(another_telegram_user, telegram_user)

    assert not is_created


@pytest.mark.django_db
@pytest.mark.unit
def test_getting_friendship_username_list(
    telegram_user: TelegramUser, another_telegram_users: List[TelegramUser], friend_requests: List[FriendRequest]
) -> None:
    actual = list(request_repo.get_usernames_to_friends(telegram_user.id))
    expected = [user.username for user in another_telegram_users]

    assert actual == expected


@pytest.mark.django_db
@pytest.mark.unit
def test_accepting_friend(
    telegram_user: TelegramUser, another_telegram_user: TelegramUser, friend_request: FriendRequest
) -> None:
    is_accepted = friend_service.try_accept_friend(another_telegram_user, telegram_user)

    assert is_accepted
    assert telegram_user.friends.filter(id=another_telegram_user.id).exists()
    assert another_telegram_user.friends.filter(id=telegram_user.id).exists()
    assert not FriendRequest.objects.filter(source=another_telegram_user, destination=telegram_user).exists()


@pytest.mark.django_db
@pytest.mark.unit
def test_accepting_friend__request_is_not_exist(
    telegram_user: TelegramUser, another_telegram_user: TelegramUser
) -> None:
    is_accepted = friend_service.try_accept_friend(another_telegram_user, telegram_user)

    assert not is_accepted
    assert not telegram_user.friends.filter(id=another_telegram_user.id).exists()
    assert not another_telegram_user.friends.filter(id=telegram_user.id).exists()
    assert not FriendRequest.objects.filter(source=another_telegram_user, destination=telegram_user).exists()


@pytest.mark.django_db
@pytest.mark.unit
def test_rejecting_friend_request(telegram_user: TelegramUser, another_telegram_user: TelegramUser) -> None:
    request = FriendRequest.objects.create(source=another_telegram_user, destination=telegram_user)

    friend_service.reject_friend_request(another_telegram_user, telegram_user)

    assert not FriendRequest.objects.filter(pk=request.pk).exists()


@pytest.mark.django_db
@pytest.mark.unit
def test_rejecting_friend_request__not_exist(telegram_user: TelegramUser, another_telegram_user: TelegramUser) -> None:
    friend_service.reject_friend_request(another_telegram_user, telegram_user)

    assert not FriendRequest.objects.filter(source=another_telegram_user, destination=telegram_user).exists()
