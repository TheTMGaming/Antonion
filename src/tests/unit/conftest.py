from typing import List

import pytest

from app.internal.models.user import TelegramUser


@pytest.fixture(scope="function")
def friends(telegram_user: TelegramUser, telegram_users: List[TelegramUser]) -> List[TelegramUser]:
    return [friend for friend in telegram_users if friend != telegram_user]
