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
from enum import IntEnum
from enum import auto
from dataclasses import field


class ETaskType(StrEnum):
    INVITE_FAMILY = 'INVITE_FAMILY'
    ASSOCIATE_FAMILY = 'ASSOCIATE_FAMILY'
    JOIN_FAMILY = 'JOIN_FAMILY'
    SHIP_OBJECT = 'SHIP_OBJECT'


class EDefaultTaskType(IntEnum):
    DEFAULT_STATE = auto()


class ERoutingStepType(IntEnum):
    BEFORE_CARRIER = auto()
    ROUTING = auto()
    GIVE_FEEDBACK = auto()


@dataclass
class TaskStep:
    task_step_type: int 
    alias_dikastes: str
    desc_dikastes: str
    alias_diakonos: str
    desc_diakonos: str
    pars: object


@dataclass
class RoutingStepData:
    agora_dest: str
    pin_to_give: int


@dataclass
class FeedbackStepData:
    token: str


@dataclass
class RoutingTaskData:
    chain_exports: list[str] = field(default_factory = list)
    chain_imports: list[str] = field(default_factory = list)


