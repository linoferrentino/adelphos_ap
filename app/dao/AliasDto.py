

from app.logging import gCon
from dataclasses import dataclass

# This is the class which models an alias in adelphos, usually this is a
# real person in the fediverse.

table_name = "alias"

# The alias seems to belong to one group: in reality he belongs to several
# groups, but we list here only the innermost group, because every group
# has only one parent, from the l-zero group we can go up to all levels.

class AdelphosObject:
    # an object in adelphos has a global identifier (which is global in all
    # the instances) and various control fields to acquire it on demand.
    pass

@dataclass
class AliasDto:

    alias_uri: str = None
    actor_fk: str = None
    group_fk: str = None
    password: str = None
    timestamp: str = None

    @staticmethod
    def get_from_alias_uri(ctx, alias_uri):

        global table_name

        fields_to_ask = ('alias_uri', 'actor_fk', 
                         'password', 'timestamp')

        field_to_seek = 'alias_uri'
        value_to_seek = alias_uri

        dto = ctx.app.dao.get_dto(table_name, fields_to_ask, field_to_seek, 
                            value_to_seek, AliasDto)
        return dto


    def store(self, ctx):
        global table_name

        fields_stored = {
                         'alias_uri': self.alias_uri,
                         'actor_fk' : self.actor_fk,
                         'password': self.password,
                         }

        ctx.app.dao.insert_dto(ctx, table_name, fields_stored)

        gCon.log(f"Created new alias {self.alias_uri}")


