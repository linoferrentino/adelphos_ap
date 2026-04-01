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
# of error, ad_errno is set to the last error.

# in case -1 is a valid answer the function will return an exception

from app.logging import gCon

# the last error encountered.
ad_errno = 0

# the object is not thread safe, however every function is a transaction.
# that is it leaves the world in a consistent state.
class Adelphos:

    def __init__(self, name, dao):
        self.name = name
        self.dao = dao


    # the aliases subsystem
    def alias_ss(self):
        return self.alias_ss


    def add_federated_adelphos(self, other_adelphos):
        pass


    # it returns the id of the new alias.
    def alias_create(self, alias_name, alias_family):
        global ad_errno

        if self.dao.get_family(alias_family) is not None:
            ad_errno = EAdCore.EDUPLICATED_FAMILY
            return -1

        fam_id = self.dao.add_family(alias_family)
        alias_id = self.dao.add_alias(alias_name, fam_id)

        return alias_id


    def get_items(self, alias_id, my_equity):
        pass
