from abc import abstractmethod
from decimal import Decimal
from typing import List

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
    def pretty_number(self) -> str:
        return " ".join(self.__get_groups())

    @property
    def short_number(self) -> str:
        groups = self.__get_groups()

        return " ".join([groups[0], "*" * self.group_number_count, groups[-1]])

    @abstractmethod
    def get_owner(self) -> TelegramUser:
        pass

    @abstractmethod
    def get_balance(self) -> Decimal:
        pass

    def __get_groups(self) -> List[str]:
        group = self.group_number_count
        str_ = str(self.number_field)

        return [str_[i * group : (i + 1) * group] for i in range(len(str_) // group)]
