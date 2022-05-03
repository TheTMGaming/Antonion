from typing import Dict, Optional, Union

from django.db import IntegrityError, transaction
from django.db.models import QuerySet

from app.internal.models.user import FriendRequest, TelegramUser
from app.internal.services.user.TelegramUserFields import TelegramUserFields


def get_friend(user: TelegramUser, identifier: Union[int, str]) -> Optional[TelegramUser]:
    param = (
        {TelegramUserFields.ID: int(identifier)}
        if str(identifier).isdigit()
        else {TelegramUserFields.USERNAME: str(identifier)}
    )

    return user.friends.filter(**param).first()


def get_friends(user: TelegramUser) -> QuerySet[TelegramUser]:
    return user.friends.all()


def get_friends_with_enums(user: TelegramUser) -> Dict[int, TelegramUser]:
    return dict((num, friend) for num, friend in enumerate(get_friends(user), 1))


def is_friend_exist(user: TelegramUser, friend: TelegramUser) -> bool:
    return user.friends.filter(pk=friend.pk).exists()


def try_create_friend_request(source: TelegramUser, destination: TelegramUser) -> bool:
    if source.friend_request_from_me.filter(destination=destination).exists():
        return False

    FriendRequest.objects.create(source=source, destination=destination)

    return True


def get_friendship_username_list(user_id: Union[int, str]) -> QuerySet[str]:
    return FriendRequest.objects.filter(destination__id=user_id).values_list("source__username", flat=True)


def try_accept_friend(source: TelegramUser, destination: TelegramUser) -> bool:
    request = FriendRequest.objects.filter(source=source, destination=destination).first()

    if not request:
        return False

    try:
        with transaction.atomic():
            source.friends.add(destination)
            destination.friends.add(source)
            request.delete()
    except IntegrityError:
        return False

    return True


def reject_friend_request(source: TelegramUser, destination: TelegramUser) -> None:
    destination.friend_request_to_me.filter(source=source).delete()


def try_remove_from_friends(first: TelegramUser, second: TelegramUser) -> bool:
    try:
        with transaction.atomic():
            first.friends.remove(second)
            second.friends.remove(first)
        return True
    except IntegrityError:
        return False
