from django.contrib import admin

from app.internal.models.telegram_info import TelegramUser


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "first_name", "last_name", "phone", "passport", "is_bot")
    list_display_links = ("id", "username")
    list_editable = ("passport",)
    readonly_fields = ("id", "username", "first_name", "last_name", "phone", "is_bot")
