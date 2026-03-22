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


# A carrier line is between two points.
# The carrier has a person who is in charge to bring the object
# from one place to another.

# it needs five people:

# the carrier
# the two people at the end of the line
# the two confirmers


@dataclass
class CarrierLineDto(FdObjectDto):

    point_a_fk: int
    alias_a_fk: int
    referee_a_fk: int

    point_b_fk: int
    alias_b_fk: int
    referee_b_fk: int

    carrier_alias_fk: int
    cost: int
    minimum_frequency: float
    limit_weight: float
    maximum_dimension: float

