from typing import List

import pytest
from django.db.models import QuerySet

from app.internal.models.user import FriendRequest, TelegramUser


@pytest.fixture(scope="function")
def friend_request(telegram_user: TelegramUser, another_telegram_user: TelegramUser) -> FriendRequest:
    return FriendRequest.objects.create(source=another_telegram_user, destination=telegram_user)


@pytest.fixture(scope="function")
def friend_requests(telegram_user: TelegramUser, telegram_users: List[TelegramUser]) -> QuerySet[FriendRequest]:
    return FriendRequest.objects.bulk_create(
        FriendRequest(source=another, destination=telegram_user)
        for another in telegram_users
        if another != telegram_user
    )
