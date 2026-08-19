######################################################
#
# Adelphos AP: the fractal trust network
#
# Activity Pub implementation
#
# © 2025-26 Lino Ferrentino
# lino.ferrentino@gmail.com
#
# This is free software. Licensed with GPL version 3
#
######################################################


from enum import IntEnum
from app.core.AdelphosCoreException import AdelphosBaseException


class EFdbErrors(IntEnum):
    FDB_OK = 0
    EFDB_NO_SUCH_TRANSACTION = 1
    EFDB_NO_LOCAL_URI = 2
    EFDB_ONLY_LOCAL_STORE = 3
    EFDB_URI_EXISTS = 4
    EFDB_NO_SUCH_OB = 5
    EFDB_NO_LOCK_ON_OB = 6
    EFDB_INVALID_VAL_TYPE = 7
    EFDB_INVALID_URIS = 8
    EFDB_UNKNOWN_TYPE = 9
    EFDB_DUPLICATED_CLASS= 10
    EFDB_DUPLICATED_COLUMN = 11
    EFDB_REQUIRED_FIELD_MISSING = 12
    EFDB_URIS_CANNOT_BE_SET_DIRECTLY = 13
    EFDB_EXTRA_FIELD = 14
    EFDB_UNKNOWN_COLUMN = 15
    EFDB_ITEARABLE_EXPECTED = 16
    EFDB_SCALAR_UNEXPECTED = 17
    EFDB_URI_NOT_EXPECTED = 18
    EFDB_SCALAR_EXPECTED = 19
    EFDB_SET_EXPECTED = 20
    EFDB_VALUE_NOT_PRESENT = 21
    EFDB_CARDINALITY_LOWER = 22
    EFDB_INVALID_ENUM_VALUE = 23
    EFDB_RESERVED = 24 
    EFDB_LENT = 25
    EFDB_URI_EXPECTED = 26
    EFDB_INVALID_STATE = 27
    EFDB_OBJECT_GONE = 28
    EFDB_READ_INCOHERENT = 29
    EFDB_MISSING_LINK_TO_DELETED_OB = 30
    EFDB_CANNOT_DETACH_A_MODIFIED_OBJECT = 31
    EFDB_CANNOT_DETACH_A_LOCKED_OBJECT = 32
    EFDB_CONFLICT_DURING_COMMIT = 33

    EFDB_INTERNAL_ERROR = 9999


class FdbException(AdelphosBaseException):

    def __init__(self, error: EFdbErrors, msg = None):
        super().__init__("Federated Db", error, msg)


