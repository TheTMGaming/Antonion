from typing import Callable, List, Union

import pytest
from django.http import HttpRequest

from app.internal.general.rest.exceptions import BadRequestException, NotFoundException
from app.internal.general.rest.responses import SuccessResponse
from app.internal.user.db.models import FriendRequest, TelegramUser
from app.internal.user.db.repositories import FriendRequestRepository, SecretKeyRepository, TelegramUserRepository
from app.internal.user.domain.entities.user import TelegramUserOut
from app.internal.user.domain.services import FriendRequestService, FriendService, TelegramUserService
from app.internal.user.presentation.handlers import FriendHandlers

user_service = TelegramUserService(user_repo=TelegramUserRepository(), secret_key_repo=SecretKeyRepository())
friend_service = FriendService(friend_repo=TelegramUserRepository())
request_service = FriendRequestService(request_repo=FriendRequestRepository())
handlers = FriendHandlers(user_service=user_service, friend_service=friend_service, request_service=request_service)


@pytest.mark.django_db
@pytest.mark.integration
def test_getting_friends(http_request: HttpRequest, friends: List[TelegramUser]) -> None:
    actual = handlers.get_friends(http_request)
    expected = http_request.telegram_user.friends.all()

    assert len(actual) == len(expected)

    actual = sorted(actual, key=lambda schema: schema.id)
    expected = sorted(expected, key=lambda user: user.id)

    for i in range(len(actual)):
        assert_users_info(actual[i], expected[i])


@pytest.mark.django_db
@pytest.mark.integration
def test_getting_friend(http_request: HttpRequest, friends: List[TelegramUser]) -> None:
    assert_get_friend_handlers_by_bad_identifier(http_request)

    for friend in http_request.telegram_user.friends.all():
        actual_by_id = handlers.get_friend(http_request, friend.id)
        assert_users_info(actual_by_id, friend)

        actual_by_username = handlers.get_friend(http_request, friend.username)
        assert_users_info(actual_by_username, friend)


@pytest.mark.django_db
@pytest.mark.integration
def test_removing_friend(http_request: HttpRequest, friends: List[TelegramUser]) -> None:
    assert_get_friend_handlers_by_bad_identifier(http_request)

    friend_1, friend_2 = friends[:2]

    actual_by_id = handlers.remove_friend(http_request, friend_1.id)
    actual_by_username = handlers.remove_friend(http_request, friend_2.username)

    assert actual_by_id == actual_by_username == SuccessResponse()
    assert not http_request.telegram_user.friends.filter(id=friend_1.id).exists()
    assert not http_request.telegram_user.friends.filter(username=friend_2.username).exists()


@pytest.mark.django_db
@pytest.mark.integration
def test_adding_friend(http_request: HttpRequest, another_telegram_users: List[TelegramUser]) -> None:
    user = http_request.telegram_user
    another_users = another_telegram_users[:2]
    user_1, user_2 = another_users

    for friend in another_users:
        user.friends.remove(friend)

    actual_by_id = handlers.add_friend(http_request, user_1.id)
    actual_by_username = handlers.add_friend(http_request, user_2.username)

    assert actual_by_id == actual_by_username == SuccessResponse()
    assert FriendRequest.objects.filter(source=user, destination_id=user_1).exists()
    assert FriendRequest.objects.filter(source=user, destination_id=user_2).exists()


@pytest.mark.django_db
@pytest.mark.integration
def test_adding_friend__invalid_identifier(http_request: HttpRequest) -> None:
    assert_getting_user_by_bad_identifier(http_request, handlers.add_friend)


@pytest.mark.django_db
@pytest.mark.integration
def test_adding_friend__user_is_already_friend(http_request: HttpRequest, friend: TelegramUser) -> None:
    assert_bad_request_in_adding_friend(http_request, friend)


@pytest.mark.django_db
@pytest.mark.integration
def test_adding_friend__request_exists(http_request: HttpRequest, another_telegram_user: TelegramUser) -> None:
    FriendRequest.objects.create(source=http_request.telegram_user, destination=another_telegram_user)

    assert_bad_request_in_adding_friend(http_request, another_telegram_user)


@pytest.mark.django_db
@pytest.mark.integration
def test_getting_friend_requests(http_request: HttpRequest, friend_requests: List[FriendRequest]) -> None:
    actual = sorted(map(lambda request: request.username, handlers.get_friend_requests(http_request)))
    expected = sorted(map(lambda request: request.source.username, friend_requests))

    assert actual == expected


@pytest.mark.django_db
@pytest.mark.integration
def test_accepting_friend_request__invalid_identifier(http_request: HttpRequest) -> None:
    assert_getting_user_by_bad_identifier(http_request, handlers.accept_friend_request)


@pytest.mark.django_db
@pytest.mark.integration
def test_accepting_friend_request__request_does_not_exist(
    http_request: HttpRequest, another_telegram_user: TelegramUser
) -> None:
    with pytest.raises(BadRequestException):
        handlers.accept_friend_request(http_request, another_telegram_user.id)
        handlers.accept_friend_request(http_request, another_telegram_user.username)


@pytest.mark.django_db
@pytest.mark.integration
def test_accepting_friend_request(
    http_request: HttpRequest, telegram_user: TelegramUser, friend_requests: List[FriendRequest]
) -> None:
    request_1, request_2 = friend_requests[0], friend_requests[1]

    actual_by_id = handlers.accept_friend_request(http_request, request_1.source.id)
    actual_by_username = handlers.accept_friend_request(http_request, request_2.source.username)

    assert actual_by_id == actual_by_username == SuccessResponse()
    assert not FriendRequest.objects.filter(pk=request_1.pk).exists()
    assert not FriendRequest.objects.filter(pk=request_2.pk).exists()
    assert telegram_user.friends.filter(id=request_1.source.id).exists()
    assert telegram_user.friends.filter(id=request_2.source.id).exists()


@pytest.mark.django_db
@pytest.mark.integration
def test_rejecting_friend_request__invalid_identifier(http_request: HttpRequest) -> None:
    assert_getting_user_by_bad_identifier(http_request, handlers.reject_friend_request)


@pytest.mark.django_db
@pytest.mark.integration
def test_rejecting_friend_request__request_does_not_exist(
    http_request: HttpRequest, another_telegram_user: TelegramUser
) -> None:
    with pytest.raises(BadRequestException):
        handlers.reject_friend_request(http_request, another_telegram_user.id)
        handlers.reject_friend_request(http_request, another_telegram_user.username)


@pytest.mark.django_db
@pytest.mark.integration
def test_rejecting_friend_request(
    http_request: HttpRequest, telegram_user: TelegramUser, friend_requests: List[FriendRequest]
) -> None:
    request_1, request_2 = friend_requests[0], friend_requests[1]

    actual_by_id = handlers.reject_friend_request(http_request, request_1.source.id)
    actual_by_username = handlers.reject_friend_request(http_request, request_2.source.username)

    assert actual_by_id == actual_by_username == SuccessResponse()
    assert not FriendRequest.objects.filter(pk=request_1.pk).exists()
    assert not FriendRequest.objects.filter(pk=request_2.pk).exists()
    assert not telegram_user.friends.filter(id=request_1.source.id).exists()
    assert not telegram_user.friends.filter(id=request_2.source.id).exists()


def assert_bad_request_in_adding_friend(http_request: HttpRequest, friend: TelegramUser) -> None:
    with pytest.raises(BadRequestException):
        handlers.add_friend(http_request, friend.id)
        handlers.add_friend(http_request, friend.username)


def assert_users_info(
    first: Union[TelegramUserOut, TelegramUser], second: Union[TelegramUserOut, TelegramUser]
) -> None:
    assert first.id == second.id
    assert first.phone == second.phone
    assert first.username == second.username
    assert first.first_name == second.first_name
    assert first.last_name == second.last_name


def assert_get_friend_handlers_by_bad_identifier(http_request: HttpRequest) -> None:
    unknown = TelegramUser.objects.create(id=0, username="hoholock", first_name="Petr", last_name="Banana")

    for bad in ["-1", unknown.id, unknown.username]:
        with pytest.raises(NotFoundException):
            handlers.get_friend(http_request, bad)


def assert_getting_user_by_bad_identifier(http_request: HttpRequest, handler: Callable) -> None:
    with pytest.raises(NotFoundException):
        handler(http_request, "-1")
