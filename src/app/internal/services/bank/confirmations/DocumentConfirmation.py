from abc import ABC, abstractmethod


class DocumentConfirmation(ABC):
    @abstractmethod
    def confirm(self) -> bool:
        pass
