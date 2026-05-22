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


from enum import StrEnum
from enum import auto


class Dependencies(StrEnum):
    SOCIAL = auto()
    SOCIAL_NET = auto()
    CLI_NET = auto()
    KERNEL = auto()
    CONFIG = auto()
    CLI_HANDLER = auto()
    TRANSPORT = auto()



