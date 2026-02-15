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

    # this is synchronous: we get first the alias, then we query the actor.



    # here we have to change the fields.
    # also in this case we do the hierarchical insert.
    def store_dict(self, dto, dto_as_dict):

        # first of all I store the base table

        new_id = super().store_dict(dto, dto_as_dict)

        dto_as_dict['local_fk'] = new_id

        self.dao.db.insert_dto_fields("fd_alias", ('local_fk', 'actor_fk',
                                                   'family_fk', 'password'), dto_as_dict)
        gCon.log(f"Created new alias {dto}")


