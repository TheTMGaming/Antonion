from decimal import Decimal

from django.db.models import F, QuerySet

from app.internal.bank.db.models import BankAccount
from app.internal.bank.domain.interfaces import IBankAccountRepository
from app.internal.users.db.models import TelegramUser


class BankAccountRepository(IBankAccountRepository):
    def get_bank_account(self, number: str) -> BankAccount:
        return BankAccount.objects.filter(number=number).first()

    def get_bank_accounts(self, user: TelegramUser) -> QuerySet[BankAccount]:
        return user.bank_accounts.all()

    def accrue(self, account: BankAccount, accrual: Decimal) -> None:
        account.balance = F("balance") + accrual
        account.save(update_fields=["balance"])

        account.refresh_from_db(fields=["balance"])

    def subtract(self, account: BankAccount, accrual: Decimal) -> None:
        self.accrue(account, -accrual)
