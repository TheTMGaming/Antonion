from django.db import models
from djmoney.models.fields import MoneyField

from app.internal.models.bank.Passport import Passport


class BankAccount(models.Model):
    number = models.BigAutoField(primary_key=True)
    passport = models.ForeignKey(Passport, on_delete=models.PROTECT)
    balance = MoneyField(decimal_places=2, max_digits=20, default=0, default_currency="RUB")
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return str(self.number)

    class Meta:
        db_table = "bank_accounts"
        verbose_name = "Bank Account"
        verbose_name_plural = "Bank Accounts"
        constraints = [models.CheckConstraint(name="check_balance", check=models.Q(balance__gte=0))]
