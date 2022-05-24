from typing import Union

from django.conf import settings
from django.db import IntegrityError, transaction
from phonenumbers import NumberParseException, PhoneNumberFormat, format_number, is_valid_number_for_region, parse
from telegram import User

from app.internal.users.domain.interfaces import ISecretKeyRepository, ITelegramUserRepository


class TelegramUserService:
    def __init__(self, user_repo: ITelegramUserRepository, secret_key_repo: ISecretKeyRepository):
        self._user_repo = user_repo
        self._secret_key_repo = secret_key_repo

    def try_set_phone(self, user_id: Union[int, str], value: str) -> bool:
        try:
            phone = parse("+7" + value[1:] if value.startswith(("7", "8")) else value)
        except NumberParseException:
            return False

        user = self._user_repo.get_user(user_id)
        if not user or not is_valid_number_for_region(phone, settings.PHONE_REGION):
            return False

        self._user_repo.update_phone(user_id, format_number(phone, PhoneNumberFormat.E164))
        # TelegramUser.objects.filter(id=user_id).update(phone=format_number(phone, PhoneNumberFormat.E164))

        return True

    def try_update_password(self, user: User, password: str) -> bool:
        try:
            self._user_repo.update_password(user.id, password)
            # TelegramUser.objects.update_password(user.id, password)

            return True
        except IntegrityError:
            return False

    def try_create_password(self, user: User, password: str, key: str, tip: str) -> bool:
        try:
            with transaction.atomic():
                self._secret_key_repo.create(user.id, key, tip)
                # SecretKey.objects.create(telegram_user_id=user.id, value=key, tip=tip)

                self._user_repo.update_password(user.id, password)
                # TelegramUser.objects.update_password(user.id, password)

            return True
        except IntegrityError:
            return False
