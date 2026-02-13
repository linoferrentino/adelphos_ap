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
class FdActorDao(BaseAdelphosDao):


    # I am initialized with the common DAO, the one
    # which stores the connection
    def __init__(self, dao):
        super().__init__(dao)


    # this is tha base method to get an "alive" object from the db.
    # This is only valid for the alive objects which have not a
    # double name: the family and the group.

    def get_from_local_name(self, name):
        pass


    # the difference from getting from uri an object and an alive
    # person is that the query is different!
    def get_from_uri(self, uri):
        pass


    def store_dict(self, dto, dto_as_dict):
        gCon.log("Store the fdActor Dao")

        # Here I can store the fd_actor table
        new_id = self.dao.db.insert_dto_fields('fd_actor',
                ('name', 'instance_fk'), dto_as_dict)
        
        gCon.log(f"FdActorDao new id {new_id}")
        dto.fd_actor_id = new_id
        return new_id

    #raw_local_query = """

    #select fdo.fd_object_id, fdo.name, fdo.creator_fk, 
    #fdo.timestamp, fda.name, fda.instance_fk, 
    #fda.timestamp, {ftbl_col_list} from {ftbl} as ftbl,
    #fd_object as fdo, fd_actor as fda
    #where (
    #(ftbl.local_fk = fdo.fd_object_id)
    #and
    #(fdo.creator_fk = fad.fd_actor_id)
    #and
    #(fda.instance_fk = 0),
    #and
    #(ftbl.local_fk = ?))

    #"""

