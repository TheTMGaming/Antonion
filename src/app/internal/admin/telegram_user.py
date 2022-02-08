from django.contrib import admin

from app.internal.models.telegram_user import TelegramUser


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'first_name', 'last_name', 'phone', 'is_bot')
