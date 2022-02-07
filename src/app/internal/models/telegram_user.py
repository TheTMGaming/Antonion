from django.db import models


class TelegramUser(models.Model):
    id = models.PositiveBigIntegerField(primary_key=True)
    username = models.CharField(max_length=127, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255, null=True)
    phone = models.CharField(max_length=15, null=True)
    is_bot = models.BooleanField(default=False)

    def __str__(self):
        return self.username
