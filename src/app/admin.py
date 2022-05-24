from django.contrib import admin

from app.internal.authentication.presentation.admin import AdminUserAdmin
from app.internal.bank.presentation.admin import BankAccountAdmin, BankCardAdmin
from app.internal.users.presentation.admin import TelegramUserAdmin

admin.site.site_title = "Bank of dream"
admin.site.site_header = "Bank of dream"
