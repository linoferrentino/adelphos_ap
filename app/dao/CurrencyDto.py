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

# this is the currency data class
# A currency in adelphos is linked to a normal currency in the outside
# world, however a user is free to create his own currency, if he likes,
#
# two parties must in any case agree to the currency used, based on
# the trust between them

# *everything* in adelphos is ultimately linked to trust.

from dataclasses import dataclass
from app.dao.FdObjectDto import FdObjectDto


@dataclass
class CurrencyDto(FdObjectDto):

    def __init__(self,  name, creator_fk, symbol, human_value):
        super().__init__(name, creator_fk)
        self.symbol = symbol
        self.human_value = human_value


    symbol: str

    human_value: float


