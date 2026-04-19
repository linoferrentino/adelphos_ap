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

# this is the basic class that holds a federated object,
# the federated db is responsible for its life cycle

# a federated object is an object which is identified by a federated uri.


# the federated object can be built from a string and serialize itself
# to a string: 

def fob_to_str(fob):
    pass


def str_to_fob(string):
    pass


class FederatedObject:


    # there are some objects which do not exist in isolation.
    # they start with a reference count of zero.
    # In adelphos the only 1st class objects are the aliases.
    # every other object is dependent (in some way or another) with an alias.
    def __init__(self, uri, ref_count = 0):
        self.ref_count = ref_count
        self.uri = uri
        # the object internally is a simple dict
        self.ob = {}
        self.version = 0
        self.ts_locked = None
        self.locked = False


    def get_primitive_value(self, val):
        pass


    # you cannot set a primitive value unless the object is locked.
    def set_primitive_value(self, key, val):
        pass

