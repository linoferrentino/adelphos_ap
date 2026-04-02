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


# there are the core errors, not given to the end user.
class EAdErrno(IntEnum):
    EDUPLICATED_FAMILY = 1


