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


# there are the core errors.
class EAdErrno(IntEnum):
    DONE_OK = 0
    EDUPLICATED_FAMILY = 1
    EINVALID_USER_OR_PASSWORD = 2

    # generic system error, this is a bug!
    ESYS = 500


