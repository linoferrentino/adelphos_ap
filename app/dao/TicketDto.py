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

# A ``ticket'' in adelphos is the representation of a journey of a sellable
# between one family to another.

from dataclasses import dataclass
from app.dao.FdObjectDto import FdObjectDto


@dataclass
class TicketDto(FdObjectDto):

    # a ticket is coupled to a sellable
    object_fk: int 

    pass


