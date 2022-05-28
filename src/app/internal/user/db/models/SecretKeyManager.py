from typing import Union

from django.conf import settings
from django.db import models
from django.db.models import QuerySet


class SecretKeyManager(models.Manager):
    def create(self, *args, **kwargs) -> QuerySet:
        value = "value"
        if value in kwargs:
            kwargs[value] = self._hash(kwargs[value])

        return super(SecretKeyManager, self).create(*args, **kwargs)

    def check_value(self, telegram_user_id: Union[int, str], value: str) -> bool:
        return self.get_queryset().filter(telegram_user_id=telegram_user_id, value=self._hash(value)).exists()

    @staticmethod
    def _hash(value: str) -> str:
        return settings.HASHER.encode(value.lower(), settings.SALT)
