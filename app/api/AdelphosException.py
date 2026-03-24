# this is the class used for the exceptions.


from enum import StrEnum
from enum import IntEnum
from enum import auto


class EAdelhposErrno_str(StrEnum):

    GENERIC_ERROR = 'No detail, sorry.'
    ERR_NO_DAEMON_FOR_HOST = 'No daemon for host {}'


class EAdelhposErrno(IntEnum):

    DONE_OK = 0
    GENERIC_USER_ERROR = auto()
    GENERIC_SERVER_ERROR = auto()
    ERR_NO_DAEMON_FOR_HOST = auto()


class AdelphosException(Exception):


    def __init__(self, msg, code: EAdelhposErrno = EAdelhposErrno.GENERIC_USER_ERROR):
        super().__init__(msg)
        self.code = code

