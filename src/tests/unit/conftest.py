from typing import List

import pytest
from django.db.models import QuerySet

from app.internal.authentication.db.models import RefreshToken
from app.internal.user.db.models import FriendRequest, TelegramUser


@pytest.fixture(scope="function")
def refresh_tokens(telegram_user: TelegramUser) -> QuerySet[RefreshToken]:
    tokens = [RefreshToken(telegram_user=telegram_user, value=i) for i in range(3)]

    return RefreshToken.objects.bulk_create(tokens)


@pytest.fixture(scope="function")
def refresh_token(refresh_tokens: QuerySet[RefreshToken]) -> RefreshToken:
    return refresh_tokens[0]
