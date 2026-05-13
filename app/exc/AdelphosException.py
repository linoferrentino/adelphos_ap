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
import re
from app.logging import gCon


class AdErrno(IntEnum):

    USER_DOES_NOT_EXIST = 1


def parse_exc(err_str):
    re_match = re.match(br"Adelphos error: #(\d*)#", err_str)
    if re_match is None:
        return -1
    return int(re_match.group(1))


class AdelphosException(Exception):


    def __init__(self, errno, msg = None):
        super().__init__(msg)
        self.errno = errno
        self.out_str = f"Adelphos error: #{errno}#"


