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

from argon2 import PasswordHasher

from app.dao.AdelphosUri import uriparse_type, EAdelphosType
from app.logging import gCon


# the object is not thread safe, however every function is a transaction.
# that is it leaves the world in a consistent state.
# I need the social object to post messages to users.
class Adelphos:

    def __init__(self, name, dao, social):
        self.name = name
        self.dao = dao
        self.social = social


    # the aliases subsystem
    def alias_ss(self):
        return self.alias_ss


    def add_federated_adelphos(self, other_adelphos):
        pass



    #def create_alias_pass(self, actor_id, alias, password):

    #    alias_uri = uriparse_type(alias, EAdelphosType.ALIAS_TYPE)

    #    if (alias_uri.is_numeric == True):
    #        raise AdelphosException("Cannot create a numeric alias")

    #    #gCon.log(f"alias uri created {alias_uri}")

    #    family_dto = self.gateway.app.dao.family_dao.get_from_local_name(
    #            alias_uri.family)

    #    if (family_dto is not None):
    #        raise AdelphosException(
#f"fa#mily {alias_uri.family} is already existing in this instance")

    #    ph = PasswordHasher()
    #    pass_hashed = ph.hash(password)

    #    # we are creating here an alias in instance zero.
    #    self.gateway.app.dao.alias_dao.create_alias_impl(
    #        actor_id, alias_uri.family, 0, alias_uri.name, pass_hashed)


    #@commit_if_ok
    def alias_uri_create(self, actor_id, alias_uri, password):

        alias_uri = uriparse_type(alias, EAdelphosType.ALIAS_TYPE)

        if (alias_uri.is_numeric == True):
            raise AdelphosException("Cannot create a numeric alias")

        self._alias_create_impl(actor_id, alias_uri.name,
            alias_uri.family, password)



    def get_items(self, alias_id, my_equity):
        pass
