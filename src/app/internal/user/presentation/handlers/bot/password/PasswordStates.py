from enum import IntEnum, auto


class PasswordStates(IntEnum):
    SECRET_CONFIRMATION = auto()
    PASSWORD_ENTERING_IN_UPDATING = auto()
    PASSWORD_CONFIRMATION_IN_UPDATING = auto()
    SECRET_CREATING = auto()
    TIP_CREATING = auto()
    PASSWORD_ENTERING_IN_CREATING = auto()
    PASSWORD_CONFIRMATION_IN_CREATING = auto()
    CONFIRMATION_OK = auto()
