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


class EDefaultTaskType(StrEnum):
    DEFAULT_STATE = auto()


class ERoutingStepType(StrEnum):
    BEFORE_CARRIER = auto()
    ROUTING = auto()
    LAST_MILE = auto()
    GIVE_FEEDBACK = auto()


@dataclass
class TaskStepData:
    dikastes_uri: str
    diakonos_uri: str


@dataclass
class GenericTaskStepData(TaskStepData):
    pars: object


@dataclass
class TaskStep:
    task_step_type: int 
    data: TaskStepData = None
    completed_on: str = None


@dataclass
class RoutingStepData(TaskStepData):
    family_dest: str
    pin_to_give: int


@dataclass
class FeedbackStepData(TaskStepData):
    pass


@dataclass
class FirstStepData(TaskStepData):
    pass


@dataclass
class LastStepData(TaskStepData):
    pass


@dataclass
class FamilyInviteData(TaskStepData):
    user_handle: str
    invite_code: str


@dataclass
class RoutingTaskData:
    #agora_exported_price: float
    #chain_exports: list[str] = field(default_factory = list)
    #chain_imports: list[str] = field(default_factory = list)
    routing: list = field(default_factory = list)



