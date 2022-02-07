from typing import Optional
from app.models import TelegramUser
from .user_info import UserInfo
import phonenumbers as pn


def try_add_user(user_id, username, first_name, last_name, is_bot) -> bool:
    obj, was_added = TelegramUser.objects.update_or_create(
        id=user_id,
        defaults={
            'username': username,
            'first_name': first_name,
            'last_name': last_name,
            'is_bot': is_bot
        }
    )

    return was_added


def get_user_info(user_id) -> Optional[UserInfo]:
    user = TelegramUser.objects.filter(id=user_id).first()

    return UserInfo(user.id, user.username,
                    user.first_name, user.last_name, user.phone, user.is_bot) if user else None


def exists(user_id) -> bool:
    obj = TelegramUser.objects.filter(id=user_id).first()

    return bool(obj)


def try_set_phone(user_id, value):
    user = TelegramUser.objects.filter(id=user_id).first()
    phone = parse_phone(value)

    if not user or not phone:
        return False

    user.phone = phone
    user.save()

    return True


def parse_phone(value: str) -> Optional[str]:
    if value[0] == '8':
        value = '+7' + value[1:]

    try:
        phone = pn.parse(value)
        return pn.format_number(phone, pn.PhoneNumberFormat.E164)
    except pn.NumberParseException:
        return None
