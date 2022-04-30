from django.contrib import admin

from app.internal.admin.bank import BankAccountAdmin, BankCardAdmin, TransactionAdmin
from app.internal.admin.user import TelegramUserAdmin

admin.site.site_title = "Bank of dream"
admin.site.site_header = "Bank of dream"
