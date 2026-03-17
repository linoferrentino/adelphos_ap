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

from dataclasses import dataclass
from app.dao.FdObjectDto import FdObjectDto


# A carrier line has a limit of weigth and dimensions, a cost and a minimum
# frequency guaranteed.

@dataclass
class CarrierLineDto(FdObjectDto):

    alias_1: int
    alias_2: int

    cost_1: int 
    cost_2: int 

    minimum_frequency: float
    limit_weight: float
    maximum_dimension: float

