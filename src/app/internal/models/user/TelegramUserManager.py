from typing import Union

from django.conf import settings
from django.db import models


class TelegramUserManager(models.Manager):
    def update_password(self, pk: Union[str, int], value: str):
        return self.get_queryset().filter(pk=pk).update(password=settings.HASHER.encode(value, settings.SALT))
