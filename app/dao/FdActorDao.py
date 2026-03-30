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

from abc import ABC
from abc import abstractmethod
from app.dao.BaseAdelphosDao import BaseAdelphosDao
from app.logging import gCon


# this is the base class for all the "alive" DAOs in adelphos
# alias, family, group
# the DAO will take the name of the view that makes the join and takes all the fields.
class FdActorDao(BaseAdelphosDao):


    # I am initialized with the common DAO, the one
    # which stores the connection
    def __init__(self, dao, view_name, constructor):
        super().__init__(dao)
        # the class is used to 
        self.view_name = view_name
        self.constructor = constructor

    # of course the local queries have instance == 0

    def _try_get_local_numeric_uri(self, uri):

        # I query from the local db, but the uri could be not local!
        if (BaseAdelphosDao._is_local_uri(uri)):
            instance_fk = 0
        else:
            # I have to get the adelphos instance.
            server_dto = self.dao.server_dao.get_from_hostname(uri.host_name)
            if (server_dto is None):
                # This is fatal. The server is not existing, so it cannot be here the object
                gCon.log(f"No server {uri.host_name}. This object {uri} cannot be here")
                return None
            instance_fk = server_dto.server_id

        sql_get = f"""
        select * from {self.view_name} where fd_actor_id = ? and instance_fk = 0
        """

        # to be implemented
        assert False

        # Now I will try to get the object.
        return None


    def _try_get_local_human_uri(self, uri):
        sql_get = f"""
        select * from {self.view_name} where name = :name and instance_fk = 0
        """
        params  = {
                'name' : uri.name
                }
        dto = self.dao.db.get_dto_from_sql(sql_get, params, self.constructor)
        #gCon.log(f"This is the dto {dto}")
        return dto


    def store_dict(self, dto, dto_as_dict):
        #gCon.log("Store the fdActor Dao")

        # Here I can store the fd_actor table
        new_id = self.dao.db.insert_dto_fields('fd_actor',
                ('name',), dto_as_dict)
        
        #gCon.log(f"FdActorDao new id {new_id}")
        dto.fd_actor_id = new_id
        return new_id



    # gets the name of the column that stores the private key.
    def get_pk_name(self):
        return 'fd_actor_id'


    # We have a table name for each DAO (at least once)
    def get_table_name(self):
        return 'fd_actor'
