from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from app.internal.models.bank.BankObject import BankObject
from app.internal.models.user.TelegramUser import TelegramUser


class BankAccount(models.Model, BankObject):
    DECIMAL_PLACES = 2
    DIGITS_COUNT = 20
    _MIN_NUMBER_VALUE = 10 ** (DIGITS_COUNT - 1)
    _GROUP_NUMBER_COUNT = 4

    number = models.CharField(primary_key=True, max_length=DIGITS_COUNT)
    balance = models.DecimalField(
        decimal_places=DECIMAL_PLACES, max_digits=DIGITS_COUNT, default=0, validators=[MinValueValidator(0)]
    )
    owner = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, related_name="bank_accounts")

    def __str__(self):
        return self.pretty_number

    def save(self, *args, **kwargs):
        if not self.pk:
            self.number = self.generate_number()
        super().save(*args, **kwargs)

    @property
    def group_number_count(self):
        return BankAccount._GROUP_NUMBER_COUNT

    @property
    def number_field(self):
        return self.number

    def generate_number(self) -> str:
        last: BankAccount = BankAccount.objects.order_by("number").last()

        return str(int(last.number) + 1 if last else BankAccount._MIN_NUMBER_VALUE)

    def get_balance(self) -> Decimal:
        return Decimal(self.balance)

    def try_add(self, value: Decimal) -> bool:
        if value <= 0:
            return False

        self.balance += value
        return True

    def try_extract(self, value: Decimal) -> bool:
        if value <= 0:
            return False

        self.balance -= value
        return True

    def save_operation(self) -> None:
        self.save()

    def get_owner(self) -> TelegramUser:
        return self.owner

    class Meta:
        db_table = "bank_accounts"
        verbose_name = "Bank Account"
        verbose_name_plural = "Bank Accounts"
        constraints = [models.CheckConstraint(name="check_balance", check=models.Q(balance__gte=0))]
