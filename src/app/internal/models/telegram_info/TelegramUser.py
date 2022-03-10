from django.db import models


class TelegramUser(models.Model):
    id = models.PositiveBigIntegerField(primary_key=True)
    username = models.CharField(max_length=127, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255, null=True)
    phone = models.CharField(max_length=15, null=True)
    is_bot = models.BooleanField(default=False)
    passport = models.ForeignKey("Passport", on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.username

    def to_dictionary(self):
        return {
            "id": self.id,
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "phone": self.phone,
            "is_bot": self.is_bot,
        }

    class Meta:
        db_table = "telegram_users"
        verbose_name = "Telegram User"
        verbose_name_plural = "Telegram Users"
