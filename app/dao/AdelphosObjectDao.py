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
# this is the base class for all the DAOs in adelphos which insist
# on inanimate objects.

from abc import ABC
from abc import abstractmethod
from app.dao.BaseAdelphosDao import BaseAdelphosDao


# the base class for the data access to the federated db in adelphos.
# this class has the logic to query the other federated instances
# the serialized representation of a remote object or to give it
# to others.
class AdelphosObjectDao(BaseAdelphosDao):


    # every federated table in the db has a 1:1 mapping with the
    # adelphos object table. Here we have the common code.
    def __init__(self, db):
        super().__init__(db)


    ## this method here is not abstract, it will create the
    ## base federated table.
    #def create_schema(self, app, cursor):
    #    pass


    # this is the query to have the local objects: remember that
    # this creates the raw local objects.
    # the actor is necessary because the actor has the instance
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



