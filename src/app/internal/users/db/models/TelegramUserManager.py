from typing import Union

from django.conf import settings
from django.db import models
from django.db.models import QuerySet


class TelegramUserManager(models.Manager):
    def update_password(self, pk: Union[str, int], value: str) -> QuerySet:
        return self.get_queryset().filter(pk=pk).update(password=self.hash(value))

    def get_by_credentials(self, username: str, password: str) -> QuerySet:
        return self.get_queryset().filter(username=username, password=self.hash(password))

    @staticmethod
    def hash(password: str) -> str:
        return settings.HASHER.encode(password, settings.SALT)
