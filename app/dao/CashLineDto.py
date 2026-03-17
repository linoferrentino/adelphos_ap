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

# the cash line is a bond between two actors that allows the
# almost instantenous transfer of wealth

from dataclasses import dataclass
from app.dao.FdObjectDto import FdObjectDto


# I can have a maximum amount of cash that I am willing to transfer for a certain cost.

@dataclass
class CashLineDto(FdObjectDto):

    alias_1: int
    alias_2: int

    limit: float
    cost: int 


