from django.db import IntegrityError, transaction
from telegram import User

from app.internal.models.user import SecretKey, TelegramUser


def is_password_exists(user: TelegramUser) -> bool:
    return user.password is not None


def is_secret_key_correct(actual: str, user: User) -> bool:
    return SecretKey.objects.check_value(user.id, actual)


def try_update_password(user: User, password: str) -> bool:
    try:
        TelegramUser.objects.update_password(user.id, password)

        return True
    except IntegrityError:
        return False


def try_create_password(user: User, password: str, key: str, tip: str) -> bool:
    try:
        with transaction.atomic():
            SecretKey.objects.create(telegram_user_id=user.id, value=key, tip=tip)

            TelegramUser.objects.update_password(user.id, password)

        return True
    except IntegrityError:
        return False


def confirm_password(actual: str, expected: str) -> bool:
    return actual == expected
