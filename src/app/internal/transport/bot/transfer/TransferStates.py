from enum import IntEnum, auto


class TransferStates(IntEnum):
    DESTINATION = auto()
    DESTINATION_DOCUMENT = auto()
    SOURCE_DOCUMENT = auto()
    ACCRUAL = auto()
    CONFIRM = auto()
