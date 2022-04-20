from typing import Callable, List
from unittest.mock import MagicMock

import pytest
from telegram import User

from app.internal.models.bank import BankAccount
from app.internal.models.user import TelegramUser
from tests.conftest import BALANCE


@pytest.fixture(scope="function")
def update(user: User) -> MagicMock:
    message = MagicMock()
    message.reply_text.return_value = None
    message.text = ""

    update = MagicMock()
    update.effective_user = user
    update.message = message

    return update


@pytest.fixture(scope="function")
def context() -> MagicMock:
    context = MagicMock()
    context.args = []
    context.user_data = dict()

    return context


@pytest.fixture(scope="function")
def friend(telegram_user_with_phone: TelegramUser, friends: List[TelegramUser]) -> TelegramUser:
    telegram_user_with_phone.friends.add(friends[0])
    return friends[0]


@pytest.fixture(scope="function")
def friend_with_account(friend: TelegramUser, friend_account: BankAccount) -> TelegramUser:
    return friend


@pytest.fixture(scope="function")
def friend_account(friend: TelegramUser) -> BankAccount:
    return BankAccount.objects.create(balance=BALANCE, owner=friend)
