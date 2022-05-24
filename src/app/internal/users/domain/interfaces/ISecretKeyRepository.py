from abc import ABC, abstractmethod
from typing import Union

from app.internal.users.db.models import SecretKey


class ISecretKeyRepository(ABC):
    @abstractmethod
    def create(self, user_id: Union[int, str], key: str, tip: str) -> SecretKey:
        pass
