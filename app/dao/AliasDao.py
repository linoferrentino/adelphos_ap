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

# The DAO for the alias
from app.dao.FdActorDao import FdActorDao
from ..logging import gCon


# this is the utility class that handles the business logic
# for an alias object.
class AliasDao(FdActorDao):

    #@staticmethod
    #def exists_local_alias(ctx, alias):

    #    cur = ctx.app.dao._conn.cursor()
    #    cur.execute("select adelphos_id from alias_local where name = ?",
    #                (alias,))
    #    row = cur.fetchone()
    #    cur.close()
    #    if (row is None):
    #        return False
    #    return True


    #def get_from_uri(ctx, alias_uri):

    #    pass


    # this method is able to query the fediverse in order to obtain the
    # object also remotely.
    #@staticmethod
    #def get_from_alias_uri(ctx, alias_uri):

    #    fields_to_ask = ('alias_uri', 'actor_fk', 
    #                     'password', 'timestamp')

    #    field_to_seek = 'alias_uri'
    #    value_to_seek = alias_uri

    #    dto = ctx.app.dao.get_dto(table_name, fields_to_ask, field_to_seek, 
    #                        value_to_seek, AliasDto)
    #    return dto


    # here we have to change the fields.
    def store(self, dto):

        fields_stored = {
                         'alias_uri': self.alias_uri,
                         'actor_fk' : self.actor_fk,
                         'password': self.password,
                         }

        ctx.app.dao.insert_dto(ctx, table_name, fields_stored)

        gCon.log(f"Created new alias {self.alias_uri}")


