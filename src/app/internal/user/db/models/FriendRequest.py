from django.db import models

from app.internal.user.db.models.TelegramUser import TelegramUser


class FriendRequest(models.Model):
    source = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, related_name="friend_request_from_me")
    destination = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, related_name="friend_request_to_me")

    class Meta:
        unique_together = ("source", "destination")
        db_table = "friend_requests"
        verbose_name = "Friend Request"
        verbose_name_plural = "Friend Requests"
