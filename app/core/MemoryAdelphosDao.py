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

# the memory DAO will store the data in memory.


from app.core.AdelphosDao import AdelphosDao
from app.dao.FamilyDto import family_dto_create
from app.dao.AliasDto import alias_dto_create_local


# The objects here belong to local instance 0
class MemoryAdelphosDao(AdelphosDao):


    def __init__(self):

        self.families_by_id = {}
        self.families_by_name = {}
        self.next_family = 1

        self.aliases_by_id = {}
        self.aliases_by_name = {}
        self.next_alias = 1


    def get_family(self, family):
        fam_dto = self.families_by_name.get(family)
        if fam_dto is None:
            return -1
        return fam_dto.fd_actor_id


    def add_family(self, family):
        fam_id = self.next_family
        self.next_family += 1
        fam_dto = family_dto_create(family, 0)
        fam_dto.fd_actor_id = fam_id
        self.families_by_id[fam_id] = fam_dto 
        self.families_by_name[family] = fam_dto
        return fam_id
    

    def add_alias(self, actor_id, alias, fam_id, password_hashed):
        alias_id = self.next_alias
        self.next_alias += 1

        alias_dto = alias_dto_create_local(alias, actor_id, fam_id, password_hashed)
        alias_dto.fd_actor_id = alias_id

        self.aliases_by_id[alias_id] = alias_dto 
        self.aliases_by_name[alias] = alias_dto 

        return alias_id


    # here it is a nop
    def commit(self):
        pass


    # here it is an exception!
    def rollback(self):
        #raise Exception("This store does not support rollback")
        pass



