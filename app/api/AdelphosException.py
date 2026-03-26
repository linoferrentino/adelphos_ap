# this is the class used for the exceptions.


from enum import StrEnum
from enum import IntEnum
from enum import auto


class EAdelhposErrno(IntEnum):

    DONE_OK = 0
    EREMOTE_ERROR = auto()
    EGENERIC_USER = auto()
    EGENERIC_SERVER = auto()
    ECOMMAND_NOT_FOUND = auto()
    ENOLOGIN = auto()
    EINVALID_USER_OR_PASSWORD = auto()
    ENO_DAEMON_FOR_HOST = auto()
    EURI_NOT_FOUND = auto()
    EREMOTE_ADELPHOS_NOT_AUTHORIZED = auto()


class AdelphosException(Exception):


    def __init__(self, msg, code: EAdelhposErrno = EAdelhposErrno.EGENERIC_USER):
        super().__init__(msg)
        self.code = code

