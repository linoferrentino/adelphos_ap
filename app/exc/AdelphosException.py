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


class AdErrno(IntEnum):

    USER_DOES_NOT_EXIST = 1



class AdelphosException(Exception):


    def __init__(self, errno, msg = None):
        super().__init__(msg)
        self.errno = errno


