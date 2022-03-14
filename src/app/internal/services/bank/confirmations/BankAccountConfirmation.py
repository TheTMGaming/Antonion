from app.internal.models.bank import BankAccount

from .DocumentConfirmation import DocumentConfirmation


class BankAccountConfirmation(DocumentConfirmation):
    def __init__(self, account: BankAccount, actual_series: int, actual_number: int):
        super(BankAccountConfirmation, self).__init__()
        self._account = account
        self._actual_series, self._actual_number = actual_series, actual_number

    def confirm(self) -> bool:
        passport = self._account.passport
        return passport.series == self._actual_series and passport.number == self._actual_number
