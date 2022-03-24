from typing import Union

from django.conf import settings
from phonenumbers import NumberParseException, PhoneNumberFormat, format_number, is_valid_number_for_region, parse
from telegram import User

from app.internal.models.telegram_info import TelegramUser


def try_add_user(user: User) -> bool:
    attributes = {
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
    }

    obj, was_added = TelegramUser.objects.update_or_create(id=user.id, defaults=attributes)

    return was_added


def get_user_info(user_id: Union[int, str]) -> TelegramUser:
    return TelegramUser.objects.filter(id=user_id).first()


def exists(user_id: Union[int, str]) -> bool:
    return bool(get_user_info(user_id))


def try_set_phone(user_id: Union[int, str], value: str) -> bool:
    try:
        phone = parse("+7" + value[1:] if value.startswith("8") else value)
    except NumberParseException:
        return False

    user = get_user_info(user_id)
    if not user or not is_valid_number_for_region(phone, settings.PHONE_REGION):
        return False

    TelegramUser.objects.filter(id=user_id).update(phone=format_number(phone, PhoneNumberFormat.E164))

    return True
