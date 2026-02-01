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
from app.dao.ActorDto import ActorDto
from app.dao.AdelphosDto import AdelphosDto


# The family is a level zero group.
# Every one does belong to a family


# this is the basic object, not with all the fields.
@dataclass
class FamilyDto:

    local_fk: int

    # every family has an equity and a currency
    currency_fk: int


    equity: float




# this is the class with all the fields.
@dataclass
class FamilyRawDto(AdelphosDto):

    pass



class FamilyDao:

    # this searches for a local family
    @staticmethod
    def get_local_family(ctx, family_name):

        cur = ctx.app.dao._conn.cursor()
        cur.execute("select * from family_local_raw where name = ?",
                    (alias,))
        row = cur.fetchone()
        cur.close()
        if (row is None):
            return None 
        return FamilyRawDto(*row) 


