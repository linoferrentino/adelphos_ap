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


# the trust line is between two actors at the same level
# That is between two families (group of level zero)
# or between two groups at outer levels.

# to start the recursion we have that the trust line is between two aliases
# but the trust is transferred to all the family 100%. This is the nature of the family.

# Adelphos is fractal in nature, so we have bonds between groups at the same level.
# bonds between different levels are not meaningful, but it is true that
# a bond between A and B on level x could be regarded as a bond between A^ and B^, the
# parent group of A and B, then also of A^^ and B^^, and so on.
from dataclasses import dataclass
#from app.dao.LineDto import LineDto


# the interest is the amount of money that you will charge to use the trust line,
# it is an annual interest.

# the currency is not defined: we use the currencies of the actors who trust themselves
# with a predefined exchange rate.

# trust is asymmetric, the two actors may have different risk attitutes.

# the trust line is /ALSO/ a credit line, because in adelphos credit and trust
# are synonimous.


@dataclass
class TrustLineDto

    # I cannot have a trust line greater than my equity!

    alias_1_fk: int
    alias_2_fk: int
    referee_fk: int

    exchange_rate_1_to_2: float

    # the maximum value for this credit, this is in decibel.
    strength_1: float

    #interest_1: float
    #interest_2: float

