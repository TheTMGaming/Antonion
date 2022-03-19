from django.contrib import admin

from app.internal.admin.bank import BankAccountAdmin, BankCardAdmin
from app.internal.admin.telegram_info import TelegramUserAdmin

admin.site.site_title = "Bank of dream"
admin.site.site_header = "Bank of dream"
