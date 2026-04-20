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
#

from enum import IntEnum

class EFdbErrors(IntEnum):
    FDB_OK = 0
    EFDB_NO_SUCH_TRANSACTION = 1
    EFDB_NO_LOCAL_URI = 2
    EFDB_ONLY_LOCAL_STORE = 3
    EFDB_URI_EXISTS = 4
    EFDB_NO_SUCH_OB = 5
    EFDB_NO_LOCK_ON_OB = 6


# I have a FdbException
class FdbException(Exception):

    def __init__(self, error: EFdbErrors, msg = None):
        super().__init__(msg)
        self.errno = error


