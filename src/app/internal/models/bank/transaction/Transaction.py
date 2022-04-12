from django.core.validators import MinValueValidator
from django.db import models

from app.internal.models.bank.transaction.TransactionTypes import TransactionTypes
from app.internal.models.user.TelegramUser import TelegramUser


class Transaction(models.Model):
    type = models.IntegerField(choices=TransactionTypes.choices, default=TransactionTypes.TRANSFER)
    source = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, related_name="transactions")
    destination = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, related_name="transactions_to_me")
    accrual = models.DecimalField(decimal_places=2, max_digits=20, default=0, validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "transactions"
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"
