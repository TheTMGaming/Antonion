from django.core.validators import MinValueValidator
from django.db import models

from app.internal.bank.db.models import BankAccount
from app.internal.bank.db.models.TransactionTypes import TransactionTypes


class Transaction(models.Model):
    type = models.IntegerField(choices=TransactionTypes.choices, default=TransactionTypes.TRANSFER)
    source = models.ForeignKey(BankAccount, on_delete=models.CASCADE, related_name="transactions_from_me")
    destination = models.ForeignKey(BankAccount, on_delete=models.CASCADE, related_name="transactions_to_me")
    accrual = models.DecimalField(decimal_places=2, max_digits=20, default=0, validators=[MinValueValidator(0)])
    photo = models.ImageField(upload_to="transactions/%Y/%m/%d/", null=True, default=None)
    was_viewed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("created_at",)
        db_table = "transactions"
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"
