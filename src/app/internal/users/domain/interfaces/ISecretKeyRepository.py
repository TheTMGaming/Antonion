from abc import ABC, abstractmethod
from typing import Union

from app.internal.users.db.models import SecretKey


class ISecretKeyRepository(ABC):
    @abstractmethod
    def create(self, user_id: Union[int, str], key: str, tip: str) -> SecretKey:
        pass

    @abstractmethod
    def is_secret_key_correct(self, user_id: Union[int, str], actual: str) -> bool:
        pass
