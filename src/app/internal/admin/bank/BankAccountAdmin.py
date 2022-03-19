from django.contrib.admin import ModelAdmin, register

from app.internal.models.bank import BankAccount


@register(BankAccount)
class BankAccountAdmin(ModelAdmin):
    list_display = ("pretty_number", "balance")
    exclude = ("number",)
