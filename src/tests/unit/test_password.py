import random
import string

import pytest
from telegram import User

from app.internal.users.db.models import SecretKey, TelegramUser
from app.internal.users.db.repositories import SecretKeyRepository, TelegramUserRepository
from app.internal.users.domain.services import TelegramUserService
from tests.conftest import KEY, TIP, WRONG_KEY

chars = string.printable
secret_key_repo = SecretKeyRepository()
user_service = TelegramUserService(user_repo=TelegramUserRepository(), secret_key_repo=secret_key_repo)
