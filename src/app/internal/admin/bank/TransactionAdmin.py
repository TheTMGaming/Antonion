from django.contrib.admin import ModelAdmin, register

from app.internal.models.bank import Transaction


@register(Transaction)
class TransactionAdmin(ModelAdmin):
    list_display = ("source", "destination", "accrual", "created_at")
