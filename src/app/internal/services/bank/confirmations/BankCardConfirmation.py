from app.internal.models.bank import BankCard

from .DocumentConfirmation import DocumentConfirmation


class BankCardConfirmation(DocumentConfirmation):
    def __init__(self, card: BankCard, actual_code: str):
        super(BankCardConfirmation, self).__init__()
        self._card = card
        self._actual_code = actual_code

    def confirm(self) -> bool:
        return BankCard.hasher.verify(self._actual_code, self._card.code)
