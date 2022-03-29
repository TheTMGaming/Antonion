from abc import abstractmethod


class GeneratedDocument:
    @property
    @abstractmethod
    def group_number_count(self):
        pass

    @property
    @abstractmethod
    def number_field(self):
        pass

    @abstractmethod
    def generate_number(self) -> int:
        pass

    @property
    def pretty_number(self):
        group = self.group_number_count
        str_ = str(self.number_field)
        return " ".join([str_[i * group : (i + 1) * group] for i in range(len(str_) // group)])
