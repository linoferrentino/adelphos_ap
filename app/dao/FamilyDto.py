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


# The family is a level zero group.
# Every one does belong to a family


# this is the basic object, not with all the fields.
@dataclass
class FamilyDto(FdActorDto):

    # every family has an equity and a currency
    currency_fk: int

    equity: float




# this is the class with all the fields, it inherits
# from both the base adelphos object and the family object.
#@dataclass
#class FamilyRawDto(AdelphosDto, FamilyDto):
#
#    pass



