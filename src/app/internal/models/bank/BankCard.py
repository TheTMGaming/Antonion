from decimal import Decimal

from django.db import models

from app.internal.models.bank.BankAccount import BankAccount
from app.internal.models.bank.BankObject import BankObject
from app.internal.models.user import TelegramUser


class BankCard(models.Model, BankObject):
    DIGITS_COUNT = 16
    _MIN_NUMBER_VALUE = 10 ** (DIGITS_COUNT - 1)
    _MAX_NUMBER_VALUE = _MIN_NUMBER_VALUE * 10 - 1
    _GROUP_NUMBER_COUNT = 4

    number = models.CharField(primary_key=True, max_length=DIGITS_COUNT)
    bank_account = models.ForeignKey(BankAccount, on_delete=models.CASCADE, related_name="bank_cards")

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

    def generate_number(self) -> str:
        last: BankCard = BankCard.objects.order_by("number").last()

        return str(int(last.number) + 1 if last else BankCard._MIN_NUMBER_VALUE)

    def get_owner(self) -> TelegramUser:
        return self.bank_account.owner

    def get_balance(self) -> Decimal:
        return self.bank_account.get_balance()

    class Meta:
        db_table = "bank_cards"
        verbose_name = "Bank Card"
        verbose_name_plural = "Bank Cards"
