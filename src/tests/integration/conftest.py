from typing import List
from unittest.mock import MagicMock

import pytest
from telegram import User

from app.internal.models.bank import BankAccount
from app.internal.models.user import TelegramUser


@pytest.fixture(scope="function")
def update(user: User) -> MagicMock:
    message = MagicMock()
    message.reply_text.return_value = None
    message.reply_document.return_value = None
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
