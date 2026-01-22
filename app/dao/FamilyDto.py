
from app.logging import gCon
from dataclasses import dataclass
from app.dao.ActorDto import ActorDto
from app.dao.AdelphosDto import AdelphosDto


# The family is a level zero group.
# Every one does belong to a family


@dataclass
class FamilyDto:


    currency_fk: int = None

    # every family has an equity and a currency
    equity: float = None


    # Then I have the possibility to have the adelphos object,
    # like for every other item.



class FamilyDao:

    # this searches for a local family
    @staticmethod
    def exists_local_family(ctx, family_name):

        cur = ctx.app.dao._conn.cursor()
        cur.execute("select adelphos_id from alias_full where name = ?",
                    (alias,))
        row = cur.fetchone()
        cur.close()
        if (row is None):
            return False
        return True


