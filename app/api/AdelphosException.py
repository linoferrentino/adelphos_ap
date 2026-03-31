# this is the class used for the exceptions.


from enum import StrEnum
from enum import IntEnum
from enum import auto


class EAdelhposErrno(IntEnum):

    DONE_OK = 0
    # not really an error, just to avoid a commit
    ECONTINUE = 1 
    EREMOTE_ERROR = 2
    EGENERIC_USER = 3
    EREMOTE_API_EXCEPTION = 5
    ECOMMAND_NOT_FOUND = 6
    ENOLOGIN = 7
    EINVALID_USER_OR_PASSWORD = 8
    ENO_DAEMON_FOR_HOST = 9
    EURI_NOT_FOUND = 10
    EREMOTE_ADELPHOS_NOT_AUTHORIZED = 11
    ELOCAL_ADELPHOS_NOT_AUTHORIZED = 12
    EBADDB = 13
    EREMOTE_URI_NOT_PRESENT = 14
    ENOROUTEFORURI = 15
    EREM_ADELPHOS_NOT_FOUND = 16
    EUNKNOW_URI_TYPE = 17

    # generic 5xx error
    EGENERIC_SERVER = 500


class AdelphosException(Exception):


    def __init__(self, msg, code: EAdelhposErrno = EAdelhposErrno.EGENERIC_USER):
        super().__init__(msg)
        self.code = code


class AdelphosRuntimeError(AdelphosException):

    def __init__(self, msg):
        super().__init__(msg, EAdelhposErrno.EGENERIC_SERVER)


def adelphos_ok_or_die(val):
    if val == True:
        return
    raise AdelphosRuntimeError("Invariant failed")

