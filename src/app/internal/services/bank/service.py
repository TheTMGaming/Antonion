from app.internal.models.bank import BankAccount, BankCard


def get_card(number: str) -> BankCard:
    return BankCard.objects.filter(number=number).first()


def get_bank_account(number: str) -> BankAccount:
    return BankAccount.objects.filter(number=number).first()


def confirm_card(card: BankCard, user_id: int) -> bool:
    return confirm_bank_account(card.bank_account, user_id)


def confirm_bank_account(account: BankAccount, user_id: int) -> bool:
    return account.owner.id == user_id


def validate_card_number(number: str) -> bool:
    return _validate_number(number, BankCard.DIGITS_COUNT)


def validate_bank_account_number(number: str) -> bool:
    return _validate_number(number, BankAccount.DIGITS_COUNT)


def _validate_number(number: str, length: int) -> bool:
    return number.isdigit() and len(number) == length
