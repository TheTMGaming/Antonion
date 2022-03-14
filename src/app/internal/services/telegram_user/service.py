from typing import Optional, Union

from phonenumbers import NumberParseException, PhoneNumberFormat, format_number, parse
from telegram import User

from app.internal.models.telegram_info import TelegramUser


def try_add_user(user: User) -> bool:
    attributes = {
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "is_bot": user.is_bot,
    }

    obj, was_added = TelegramUser.objects.update_or_create(id=user.id, defaults=attributes)

    return was_added


def get_user_info(user_id: Union[int, str]) -> Optional[TelegramUser]:
    return TelegramUser.objects.filter(id=user_id).first()


def exists(user_id: Union[int, str]) -> bool:
    return bool(get_user_info(user_id))


def try_set_phone(user_id: Union[int, str], value: str) -> bool:
    user = get_user_info(user_id)
    phone = _parse_phone(value)

    if not user or not phone:
        return False

    TelegramUser.objects.filter(id=user_id).update(phone=phone)

    return True


def _parse_phone(value: str) -> Optional[str]:
    if value.startswith("8"):
        value = "+7" + value[1:]

    try:
        phone = parse(value)
        return format_number(phone, PhoneNumberFormat.E164)
    except NumberParseException:
        return None
