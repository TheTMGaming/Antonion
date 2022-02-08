from app.models import TelegramUser

from typing import Optional, Union
from collections import namedtuple

import telegram
import phonenumbers as pn


UserInfo = namedtuple('UserInfo', ['id', 'username', 'first_name', 'last_name', 'phone', 'is_bot'])


def try_add_user(user: telegram.User) -> bool:
    obj, was_added = TelegramUser.objects.update_or_create(
        id=user.id,
        defaults={
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_bot': user.is_bot
        }
    )

    return was_added


def get_user_info(user_id: Union[int, str]) -> Optional[UserInfo]:
    user = TelegramUser.objects\
        .filter(id=user_id)\
        .first()
    if not user:
        return None

    return UserInfo(user.id, user.username,
                    user.first_name, user.last_name,
                    user.phone, user.is_bot)


def exists(user_id: Union[int, str]) -> bool:
    return bool(get_user_info(user_id))


def try_set_phone(user_id: Union[int, str], value: str) -> bool:
    user = get_user_info(user_id)
    phone = _parse_phone(value)

    if not user or not phone:
        return False

    TelegramUser.objects\
        .filter(id=user_id)\
        .update(phone=phone)

    return True


def _parse_phone(value: str) -> Optional[str]:
    if len(value) > 0 and value[0] == '8':
        value = '+7' + value[1:]

    try:
        phone = pn.parse(value)
        return pn.format_number(phone, pn.PhoneNumberFormat.E164)
    except pn.NumberParseException:
        return None
