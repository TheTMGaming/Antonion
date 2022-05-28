from typing import Union

from app.internal.user.db.models import SecretKey
from app.internal.user.domain.interfaces import ISecretKeyRepository


class SecretKeyRepository(ISecretKeyRepository):
    def is_secret_key_correct(self, user_id: Union[int, str], actual: str) -> bool:
        return SecretKey.objects.check_value(user_id, actual)

    def create(self, user_id: Union[int, str], key: str, tip: str) -> SecretKey:
        return SecretKey.objects.create(telegram_user_id=user_id, value=key, tip=tip)
