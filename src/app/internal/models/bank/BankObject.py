from abc import abstractmethod
from decimal import Decimal

from app.internal.models.user import TelegramUser


class BankObject:
    @property
    @abstractmethod
    def group_number_count(self):
        pass

    @property
    @abstractmethod
    def number_field(self):
        pass

    @abstractmethod
    def generate_number(self) -> str:
        pass

    @property
    def pretty_number(self):
        group = self.group_number_count
        str_ = str(self.number_field)
        return " ".join([str_[i * group : (i + 1) * group] for i in range(len(str_) // group)])

    @abstractmethod
    def get_owner(self) -> TelegramUser:
        pass

    @abstractmethod
    def get_balance(self) -> Decimal:
        pass
