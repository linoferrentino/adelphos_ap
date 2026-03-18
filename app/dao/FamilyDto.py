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
# The family in adelphos is the base for the fractal trust network


from app.logging import gCon
from dataclasses import dataclass
from app.dao.FdActorDto import FdActorDto
from app.dao.BaseGroupDto import BaseGroupDto


# The family is a level zero group.
# Every one does belong to a family


@dataclass
class FamilyDto(BaseGroupDto):

    # this class is only a place holder.
    pass


# this is the constructor for a family.
# it needs less fields, some will be initialized by the database 
def family_dto_create_local(name):

    # the family has level zero

    fam_dto = FamilyDto(
            None, name, 0, None, #fd_actor fields
            None, None, None, None, 0)

    return fam_dto



