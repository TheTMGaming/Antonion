from django.contrib.admin import ModelAdmin, register

from app.internal.models.bank import BankCard


@register(BankCard)
class BankCardAdmin(ModelAdmin):
    list_display = ("number", "bank_account", "passport", "code", "created_at", "closed_at")
