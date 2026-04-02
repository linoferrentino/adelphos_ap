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
# This is the base class of all the world in Adelphos
# this is agnostic relative to the interface above (GUI or CLI)
# and the implementation below (which can be a DB or anything else)

# It contains only the logic of the fractal trust network

# no authorization or authentication is done here, the class
# assumes that these are handled at outer layers.

# usually the functions in this class return 0 on OK, -errno in case
# of error 

# in case a negative value is a valid answer the function will return None
# and the last error is set in the object.

# each action is part of a transaction.

from app.logging import gCon
from app.core.EAdErrno import EAdErrno

def commit_if_ok(func):

    def internal_commit(self, *kwargs):
        try:
            res = func(self, *kwargs)
            self.dao.commit()
            return res 
        except Exception as ex:
            self.dao.rollback()
            return -self.errno

    return internal_commit



# the object is not thread safe, however every function is a transaction.
# that is it leaves the world in a consistent state.
# I need the social object to post messages to users.
class Adelphos:

    def __init__(self, name, dao, social):
        self.name = name
        self.dao = dao
        self.social = social
        self.errno = 0


    # the aliases subsystem
    def alias_ss(self):
        return self.alias_ss


    def add_federated_adelphos(self, other_adelphos):
        pass


    #@commit_if_ok
    def alias_uri_create(self, actor_id, alias_uri, password):
        pass


    # it returns the id of the new alias.
    @commit_if_ok
    def alias_create(self, actor_id, alias_name, alias_family, password_clear):
        return self._alias_create_impl(actor_id, alias_name, alias_family, password_clear)


    def _alias_create_impl(self, actor_id, alias_name, alias_family, password_clear):
        fam_id = self.dao.get_family(alias_family)
        if fam_id > 0:
            self.errno = EAdErrno.EDUPLICATED_FAMILY
            raise Exception()

        password_hashed = " " + password_clear

        fam_id = self.dao.add_family(alias_family)
        alias_id = self.dao.add_alias(actor_id, alias_name, fam_id, password_hashed)
        self.dao.commit()

        return alias_id


    def get_items(self, alias_id, my_equity):
        pass
