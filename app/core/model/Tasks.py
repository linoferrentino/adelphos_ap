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

from dataclasses import dataclass
from app.logging import gCon



@dataclass
class Task:
    pass


class RoutingStepTask:

    pin_to_receive: int
    unlock_pin_to_give: int
    pin_to_give_next_step: int
    unlocked_pin_to_receive: int
    offer_uri: str
    export_to: str
    export_referent: str
    item_title: str
    item_desc: str


class AcceptItemTask:
    pin_to_receive: int
    offer_uri: str

