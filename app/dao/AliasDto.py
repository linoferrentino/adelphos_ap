

from app.logging import gCon
from dataclasses import dataclass
from app.dao.ActorDto import ActorDto
from app.dao.AdelphosDto import AdelphosDto

# This is the class which models an alias in adelphos, usually this is a
# real person in the fediverse.

table_name = "alias"

# The alias seems to belong to one group: in reality he belongs to several
# groups, but we list here only the innermost group, because every group
# has only one parent, from the l-zero group we can go up to all levels.


@dataclass
class AliasDto(AdelphosDto):

    # the name is migrated to the base class.
    #alias: str = None

    # every local alias is linked to an actor in activity pub.
    actor_fk: int = 0

    # every alias is linked to a family, level zero.
    #family_fk: FamilyDto = None
    family_fk: int = 0

    password: str = None


# this is the utility class that handles the business logic
# for an alias object.
class AliasDao:

    @staticmethod
    def exists_local_alias(ctx, alias):

        cur = ctx.app.dao._conn.cursor()
        cur.execute("select local_fk from alias_data where alias = ?",
                    (alias,))
        row = cur.fetchone()
        cur.close()
        if (row is None):
            return False
        return True


    def get_from_uri(ctx, alias_uri):

        pass



    # this method is able to query the fediverse in order to obtain the
    # object also remotely.
    @staticmethod
    def get_from_alias_uri(ctx, alias_uri):

        fields_to_ask = ('alias_uri', 'actor_fk', 
                         'password', 'timestamp')

        field_to_seek = 'alias_uri'
        value_to_seek = alias_uri

        dto = ctx.app.dao.get_dto(table_name, fields_to_ask, field_to_seek, 
                            value_to_seek, AliasDto)
        return dto


    def store(self, ctx):

        fields_stored = {
                         'alias_uri': self.alias_uri,
                         'actor_fk' : self.actor_fk,
                         'password': self.password,
                         }

        ctx.app.dao.insert_dto(ctx, table_name, fields_stored)

        gCon.log(f"Created new alias {self.alias_uri}")


