
from app.logging import gCon
from dataclasses import dataclass
from app.dao.ActorDto import ActorDto
from app.dao.AdelphosDto import AdelphosDto


# The family is a level zero group.
# Every one does belong to a family


# this is the basic object, not with all the fields.
@dataclass
class FamilyDto:


    currency_fk: int = None

    # every family has an equity and a currency
    equity: float = None

    # Then I have the possibility to have the adelphos object,
    # like for every other item.




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


