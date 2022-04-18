from typing import List
from unittest.mock import MagicMock

import pytest
from telegram import User

from app.internal.models.user import TelegramUser


@pytest.fixture(scope="function")
def update(user: User) -> MagicMock:
    message = MagicMock()
    message.reply_text.return_value = None

    update = MagicMock()
    update.effective_user = user
    update.message = message

    return update


@pytest.fixture(scope="function")
def context(*args) -> MagicMock:
    context = MagicMock()
    context.args = []

    return context


@pytest.fixture(scope="function")
def telegram_users_with_phone(telegram_users: List[TelegramUser], phone="+78005553535") -> List[TelegramUser]:
    for user in telegram_users:
        user.phone = phone
        user.save()

    return telegram_users


@pytest.fixture(scope="function")
def telegram_user_with_phone(telegram_users_with_phone: List[TelegramUser]):
    return telegram_users_with_phone[0]
