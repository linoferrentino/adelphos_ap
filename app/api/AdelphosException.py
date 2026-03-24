# this is the class used for the exceptions.


from enum import StrEnum
from enum import IntEnum
from enum import auto


class EAdelhposErrno(IntEnum):

    DONE_OK = 0
    EGENERIC_USER = auto()
    EGENERIC_SERVER = auto()
    EINVALID_USER_OR_PASSWORD = auto()
    ENO_DAEMON_FOR_HOST = auto()
    EURI_NOT_FOUND = auto()


class AdelphosException(Exception):


    def __init__(self, msg, code: EAdelhposErrno = EAdelhposErrno.EGENERIC_USER):
        super().__init__(msg)
        self.code = code

