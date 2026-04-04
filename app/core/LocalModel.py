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

# the local model is the class that has the logic to
# handle the core of adelphos
# the fractal trust network, the exchange of credits

# it has not a concept of a social network, this
# is on another layer on top of it.

from app.dao.FamilyDao import FamilyDao
from app.dao.AliasDao import AliasDao
from app.core.EAdErrno import EAdErrno
from app.core.FamilyModel import FamilyModel
from app.core.AliasModel import AliasModel
from app.core.BaseModel import AD_INVALID_ID
from app.core.BaseModel import BaseModel
from app.logging import gCon
import traceback
from argon2 import PasswordHasher


# the local model is always consistent. Every method called
# is part of a transaction.

def commit_if_ok(func):

    def internal_commit(self, *kwargs):
        try:
            res = func(self, *kwargs)
            self.db.commit()
            return res 
        except Exception as ex:
            traceback.print_exc()
            self.db.rollback()
            return -self.errno

    return internal_commit



# the local mode uses the URI as the identifier.

# the objects do NOT cross the boundary of the model,
# at the external we only see IDs or objects created from the basic objects.

class LocalModel:


    # I have an instance id, an integer, this is then used to store the data in the same
    # db without clashes.
    def __init__(self, instance_id, db):
        self.db = db 
        self.instance_id = instance_id
        self.family_model  = FamilyModel(self.db)
        self.alias_model   = AliasModel(self.db)
        self.errno = 0


    @commit_if_ok
    def alias_create(self, actor_id, alias_name, alias_family, password_clear):
        return self._alias_create_impl(actor_id, alias_name, alias_family, password_clear)


    # it returns the id of the new alias.
    def _alias_create_impl(self, actor_id, alias_name, alias_family, password_clear):

        fam_id = self.family_model.open_name_id(alias_family)

        if fam_id != AD_INVALID_ID:
            self.errno = EAdErrno.EDUPLICATED_FAMILY
            raise Exception()

        ph = PasswordHasher()
        pass_hashed = ph.hash(password_clear)

        fam_ob = self.family_model.create(alias_family)
        alias_ob = self.alias_model.create(actor_id, alias_name, fam_ob, pass_hashed)

        self.family_model.set_boss(fam_ob, alias_ob)

        return BaseModel.get_id(alias_ob)


