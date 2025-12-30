

from app.logging import gCon
from dataclasses import dataclass

# This is the class which models an alias in adelphos, usually this is a
# real person in the fediverse.

table_name = "alias"

@dataclass
class AliasDto:

    alias_id: int = 0
    actor_fk: int = 0
    alias: str = None
    password: str = None
    date_created: str = None

    @staticmethod
    def get_from_alias(ctx, alias):

        global table_name

        fields_to_ask = ('alias_id', 'actor_fk', 
                         'alias', 'password', 'date_created')
        field_to_seek = 'alias'
        value_to_seek = alias 

        dto = ctx.app.dao.get_dto(table_name, fields_to_ask, field_to_seek, 
                            value_to_seek, AliasDto)
        return dto


    def store(self, ctx):
        global table_name

        fields_stored = {'actor_fk' : self.actor_fk,
                         'alias': self.alias,
                         'password': self.password}

        new_id = ctx.app.dao.insert_dto(ctx, table_name, fields_stored)

        gCon.log(f"Created new alias {self.alias} with id {new_id}")

        self.alias_id = new_id





