from django.db import models

from app.internal.users.db.models.TelegramUser import TelegramUser


class RefreshToken(models.Model):
    value = models.CharField(max_length=255, primary_key=True)
    telegram_user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, related_name="refresh_tokens")
    created_at = models.DateTimeField(auto_now_add=True)
    revoked = models.BooleanField(default=False)

    class Meta:
        db_table = "refresh_tokens"
        verbose_name = "Refresh Token"
        verbose_name_plural = "Refresh Tokens"
