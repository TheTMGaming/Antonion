from django.contrib.admin import ModelAdmin, register

from app.internal.models.bank import BankAccount


@register(BankAccount)
class BankAccountAdmin(ModelAdmin):
    list_display = ("number", "passport", "balance", "created_at")
    exclude = ("balance",)
