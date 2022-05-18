from rest_framework import serializers

from app.internal.models.user import TelegramUser


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramUser
        exclude = ["friends"]
