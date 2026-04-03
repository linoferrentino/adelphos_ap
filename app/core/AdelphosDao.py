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

# the base abstract class that allows the persistence of
# the objects in adelphos

from abc import ABC, abstractmethod
from app.dao.FamilyDao import FamilyDao
from app.dao.AliasDao import AliasDao



# this is the local adelphos dao, not federated. All the methods are 
# def not async def. So we do not have the ActivityPub part.

# the other class is the MasterAdelphosDao which has the async part.
# this is not abstract. It uses a store which can be implemented in
# various ways.
class AdelphosDao:


    # the dao uses a store, a db. That Db is used in two parts
    # in adelphos, in the local part and in the federated part
    def __init__(self, db):
        self.db = db 
        self.family_dao  = FamilyDao(self)
        self.alias_dao   = AliasDao(self)


    def alias_dao():
        pass

    
    #@abstractmethod
    def get_family(self, family):
        fam_dto = self.db.get_family_by_name(family)
        if fam_dto is None:
            return -1
        return fam_dto.fd_actor_id


    #@abstractmethod
    def add_family(self, family):
        pass


    #@abstractmethod
    def commit(self):
        pass


    #@abstractmethod
    def rollback(self):
        pass



