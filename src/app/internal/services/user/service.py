from typing import Union

from django.conf import settings
from phonenumbers import NumberParseException, PhoneNumberFormat, format_number, is_valid_number_for_region, parse
from telegram import User

from app.internal.models.user import TelegramUser
from app.internal.services.user.TelegramUserFields import TelegramUserFields


def try_add_user(user: User) -> bool:
    attributes = {
        TelegramUserFields.USERNAME: user.username,
        TelegramUserFields.FIRST_NAME: user.first_name,
        TelegramUserFields.LAST_NAME: user.last_name,
    }

    obj, was_added = TelegramUser.objects.update_or_create(id=user.id, defaults=attributes)

    return was_added


def get_user(identifier: Union[int, str]) -> TelegramUser:
    param = (
        {TelegramUserFields.ID: int(identifier)}
        if str(identifier).isdigit()
        else {TelegramUserFields.USERNAME: str(identifier)}
    )

    return TelegramUser.objects.filter(**param).first()


def exists_user(user_id: Union[int, str]) -> bool:
    return bool(get_user(user_id))


def try_set_phone(user_id: Union[int, str], value: str) -> bool:
    try:
        phone = parse("+7" + value[1:] if value.startswith("8") else value)
    except NumberParseException:
        return False

    user = get_user(user_id)
    if not user or not is_valid_number_for_region(phone, settings.PHONE_REGION):
        return False

    TelegramUser.objects.filter(id=user_id).update(phone=format_number(phone, PhoneNumberFormat.E164))

    return True
