from typing import Callable, List
from unittest.mock import MagicMock

import pytest
from django.http import HttpRequest
from telegram import User

from app.internal.bank.db.models import BankAccount
from app.internal.user.db.models import TelegramUser


@pytest.fixture(scope="function")
def update(user: User) -> MagicMock:
    delete = MagicMock()
    delete.return_value = None

    message = MagicMock()
    message.reply_text.return_value = None
    message.reply_document.return_value = None
    message.text = ""
    message.delete = delete

    update = MagicMock()
    update.effective_user = user
    update.message = message

    return update


@pytest.fixture(scope="function")
def http_request() -> HttpRequest:
    request = MagicMock()
    request.headers = {}

    return request


@pytest.fixture(scope="function")
def context() -> MagicMock:
    context = MagicMock()
    context.args = []
    context.user_data = dict()

    bot = MagicMock()
    bot.send_message.return_value = None
    context.bot = bot

    return context


@pytest.fixture(scope="function")
def friend(friends: List[TelegramUser]) -> TelegramUser:
    return friends[0]


@pytest.fixture(scope="function")
def friend_with_account(friend: TelegramUser, friend_account: BankAccount) -> TelegramUser:
    return friend
