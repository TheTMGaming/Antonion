from unittest.mock import MagicMock

import pytest
from django.http import HttpRequest

from app.internal.user.db.models import TelegramUser


@pytest.fixture(scope="function")
def http_request(telegram_user_with_phone: TelegramUser) -> HttpRequest:
    request = MagicMock()

    request.headers = {}
    request.telegram_user = telegram_user_with_phone

    return request
