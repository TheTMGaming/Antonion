from app.internal.bank.db.models import BankAccount, BankCard, BankObject


class BankObjectService:
    def get_bank_account_from_document(self, document: BankObject) -> BankAccount:
        if isinstance(document, BankAccount):
            return document

        if isinstance(document, BankCard):
            return document.bank_account

        raise ValueError()
