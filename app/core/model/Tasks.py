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
from dataclasses import field
from app.logging import gCon
from enum import StrEnum


class ETaskType(StrEnum):
    INVITE_FAMILY = 'INVITE_FAMILY'
    ASSOCIATE_FAMILY = 'ASSOCIATE_FAMILY'
    JOIN_FAMILY = 'join'
    SHIP_OBJECT = 'ship'


@dataclass
class TaskStep:
    desc_check_step: str
    desc_do_step: str
    pars: object


@dataclass
class Task:
    task_type : ETaskType
    expiry_date: str
    steps: list[TaskStep] = field(default_factory = list)


@dataclass
class InviteFediverseUserStep:
    user_handle: str
    invite_code: str


@dataclass
class ShippingObjectStep:
    pin_to_receive: int



