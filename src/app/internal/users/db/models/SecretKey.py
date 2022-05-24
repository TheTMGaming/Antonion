from django.db import models

from app.internal.users.db.models.SecretKeyManager import SecretKeyManager
from app.internal.users.db.models.TelegramUser import TelegramUser


class SecretKey(models.Model):
    telegram_user = models.OneToOneField(TelegramUser, on_delete=models.CASCADE, related_name="secret_key")
    value = models.CharField(max_length=255)
    tip = models.CharField(max_length=255)

    objects = SecretKeyManager()

    def __str__(self):
        return str(self.value)

    class Meta:
        db_table = "secret_keys"
        verbose_name = "Secret Key"
        verbose_name_plural = "Secret Keys"
