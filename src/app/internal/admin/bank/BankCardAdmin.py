from django.contrib.admin import ModelAdmin, register

from app.internal.models.bank import BankCard, Transaction


@register(BankCard)
class BankCardAdmin(ModelAdmin):
    list_display = ("pretty_number", "bank_account")
    exclude = ("number",)


@register(Transaction)
class TransactionAdmin(ModelAdmin):
    list_display = ("source", "destination", "accrual")
