from django.contrib.admin import ModelAdmin, register

from app.internal.models.bank import BankCard


@register(BankCard)
class BankCardAdmin(ModelAdmin):
    list_display = ("pretty_number", "bank_account")
    exclude = ("number",)
