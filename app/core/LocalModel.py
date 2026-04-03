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
from app.logging import gCon
import traceback


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




class LocalModel:


    # I have an instance id, an integer, this is then used to store the data in the same
    # db without clashes.
    def __init__(self, instance_id, db):
        self.db = db 
        self.instance_id = instance_id
        self.family_dao  = FamilyDao(self)
        self.alias_dao   = AliasDao(self)
        self.errno = 0


    @commit_if_ok
    def alias_create(self, actor_id, alias_name, alias_family, password_clear):
        return self._alias_create_impl(actor_id, alias_name, alias_family, password_clear)


    # it returns the id of the new alias.
    def _alias_create_impl(self, actor_id, alias_name, alias_family, password_clear):

        fam_id = self.family_dao.get_from_name(alias_family)

        if fam_dto is not None:
            self.errno = EAdErrno.EDUPLICATED_FAMILY
            raise Exception()

        ph = PasswordHasher()
        pass_hashed = ph.hash(password_clear)

        fam_dto = self.family_dao.create(alias_family)
        alias_dto = self.alias_dao.create(actor_id, alias_name, fam_id, pass_hashed)

        self.family_dao.update(fam_dto, EFamilyDtoFields, alias_dto.fd_actor_id)

        return 99
        return alias_id


