from typing import Union

from django.conf import settings

from app.internal.user.db.models import SecretKey
from app.internal.user.domain.interfaces import ISecretKeyRepository


class SecretKeyRepository(ISecretKeyRepository):
    def is_secret_key_correct(self, user_id: Union[int, str], actual: str) -> bool:
        return SecretKey.objects.filter(telegram_user_id=user_id, value=self._hash(actual)).exists()

    def create(self, user_id: Union[int, str], key: str, tip: str) -> SecretKey:
        return SecretKey.objects.create(telegram_user_id=user_id, value=self._hash(key), tip=tip)

    @staticmethod
    def _hash(value: str) -> str:
        return settings.HASHER.encode(value.lower(), settings.SALT)
