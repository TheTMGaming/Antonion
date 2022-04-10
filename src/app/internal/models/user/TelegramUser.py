from django.db import models


class TelegramUser(models.Model):
    id = models.PositiveBigIntegerField(primary_key=True)
    username = models.CharField(max_length=127, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255, null=True)
    phone = models.CharField(max_length=15, null=True)
    friends = models.ManyToManyField("self", symmetrical=False)

    def __str__(self):
        return str(self.username)

    def to_dictionary(self):
        return {
            "id": self.id,
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "phone": self.phone,
        }

    class Meta:
        db_table = "telegram_users"
        verbose_name = "Telegram User"
        verbose_name_plural = "Telegram Users"
