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


# this is the base class for all the "alive" DAOs in adelphos
# alias, family, group
class FdActorDao(BaseAdelphosDao):


    # I am initialized with the common DAO, the one
    # which stores the connection
    def __init__(self, dao, ftbl, ftbl_col_list):
        super().__init__(dao, ftbl, ftbl_col_list)


    # the difference from getting from uri an object and an alive
    # person is that the query is different!
    def get_from_uri(self, uri):
        pass


    raw_local_query = """

    select fdo.fd_object_id, fdo.name, fdo.creator_fk, 
    fdo.timestamp, fda.name, fda.instance_fk, 
    fda.timestamp, {ftbl_col_list} from {ftbl} as ftbl,
    fd_object as fdo, fd_actor as fda
    where (
    (ftbl.local_fk = fdo.fd_object_id)
    and
    (fdo.creator_fk = fad.fd_actor_id)
    and
    (fda.instance_fk = 0),
    and
    (ftbl.local_fk = ?))

    """

