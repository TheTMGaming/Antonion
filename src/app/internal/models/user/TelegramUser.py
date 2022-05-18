from django.db import models

from app.internal.models.user.TelegramUserManager import TelegramUserManager


class TelegramUser(models.Model):
    id = models.PositiveBigIntegerField(primary_key=True)
    username = models.CharField(max_length=127, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255, null=True)
    phone = models.CharField(max_length=15, null=True)
    password = models.CharField(max_length=255, null=True)
    friends = models.ManyToManyField("self", symmetrical=True)

    objects = TelegramUserManager()

    def __str__(self):
        return str(self.username)

    class Meta:
        db_table = "telegram_users"
        verbose_name = "Telegram User"
        verbose_name_plural = "Telegram Users"
