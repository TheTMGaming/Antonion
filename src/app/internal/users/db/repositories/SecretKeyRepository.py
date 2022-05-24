from typing import Union

from telegram import User

from app.internal.users.db.models import SecretKey
from app.internal.users.domain.interfaces import ISecretKeyRepository


class SecretKeyRepository(ISecretKeyRepository):
    def is_secret_key_correct(self, actual: str, user: User) -> bool:
        return SecretKey.objects.check_value(user.id, actual)

    def create(self, user_id: Union[int, str], key: str, tip: str) -> SecretKey:
        return SecretKey.objects.create(telegram_user_id=user_id, value=key, tip=tip)
