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
    CLI_NET = auto()
    CLI_HANDLER = auto()
    TRANSPORT = auto()
    SOCIAL = auto()
    SOCIAL_GATEWAY = auto()
    SOCIAL_NET = auto()
    SOCIAL_DAO = auto()
    BACKDOOR_NET = auto()
    SOCIAL_API = auto()
    RPC_API = auto()
    INBOX_API = auto()
    CLI_API = auto()

