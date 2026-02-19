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
# This is the base class for the groups and families in adelphos


from app.logging import gCon
from dataclasses import dataclass
from dataclasses import field
from app.dao.FdActorDto import FdActorDto


# this is the dataclass used to create a new object.
@dataclass
class BaseGroupDto(FdActorDto):

    parent_group_fk: int

    boss_fk: int

    cashier_fk: int

    judge_fk: int

    currency_fk: int 

    # equity and currenct can be set after: now we simply set the name
    equity: float

    level: int

