from django.contrib.admin import ModelAdmin, register

from app.internal.bank.db.models import BankAccount


@register(BankAccount)
class BankAccountAdmin(ModelAdmin):
    list_display = ("pretty_number", "balance", "owner")
    exclude = ("number",)
