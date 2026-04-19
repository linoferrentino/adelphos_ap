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

from dataclasses import dataclass
from dataclasses import asdict
import dataclasses
from datetime import datetime
import json

# this is the basic class that holds a federated object,
# the federated db is responsible for its life cycle

# a federated object is an object which is identified by a federated uri.


# the federated object can be built from a string and serialize itself
# to a string: 

#def fob_to_str(fob):
#    pass
#
#

def str_to_fob(uri_ob, str_ob):
    ob = json.loads(str_ob)
    fob = FederatedObject(uri_ob, ob = ob)
    return fob



# the schema is free: we do not enforce a schema, derived classes should do that
# this is the object as it is stored permanently
@dataclass
class FObSerialized:
    version: int
    ref_count: int
    # remember to create the dictionary as a default field.
    fields = dict()


class FederatedObject:

    ts_locked: datetime
    locked: bool

    # there are some objects which do not exist in isolation.
    # they start with a reference count of zero.
    # In adelphos the only 1st class objects are the aliases.
    # every other object is dependent (in some way or another) with an alias.
    def __init__(self, uri, ref_count = 0, ob = None):
        self.uri = uri
        # the object internally is a simple dict
        self.ob = FObSerialized(0, ref_count)
        self.ts_locked = None


    # gives a string representation of the object suitable to be
    # serialized to the store.
    def to_store_str(self):
        return json.dumps(asdict(self.ob))


    def get_primitive_value(self, val):
        pass


    # you cannot set a primitive value unless the object is locked.
    def set_primitive_value(self, key, val):
        pass

