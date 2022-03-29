from django.db import models

from app.internal.models.bank.BankAccount import BankAccount
from app.internal.models.bank.GeneratedDocument import GeneratedDocument


class BankCard(models.Model, GeneratedDocument):
    DIGITS_COUNT = 16
    _MIN_NUMBER_VALUE = 10 ** (DIGITS_COUNT - 1)
    _MAX_NUMBER_VALUE = _MIN_NUMBER_VALUE * 10 - 1
    _GROUP_NUMBER_COUNT = 4

    number = models.CharField(primary_key=True, max_length=DIGITS_COUNT)
    bank_account = models.ForeignKey(BankAccount, on_delete=models.CASCADE)

    def __str__(self):
        return self.pretty_number

    def save(self, *args, **kwargs):
        if not self.pk:
            self.number = self.generate_number()
        super().save(*args, **kwargs)

    @property
    def group_number_count(self):
        return BankCard._GROUP_NUMBER_COUNT

    @property
    def number_field(self):
        return self.number

    def generate_number(self) -> int:
        last: BankCard = BankCard.objects.order_by("number").last()
        if not last:
            return BankCard._MIN_NUMBER_VALUE

        return int(last.number) + 1

    class Meta:
        db_table = "bank_cards"
        verbose_name = "Bank Card"
        verbose_name_plural = "Bank Cards"
