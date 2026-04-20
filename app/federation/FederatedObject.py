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
from dataclasses import field
import dataclasses
from datetime import datetime
import json
from app.logging import gCon

from app.federation.FdbException import FdbException
from app.federation.FdbException import EFdbErrors

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
    #gCon.log(f"loading from {str_ob}")
    ob = json.loads(str_ob)
    #gCon.log(f"the ob is {ob}")
    fob = FederatedObject(uri_ob, ob = ob, locked = False)
    return fob



# the schema is free: we do not enforce a schema, derived classes should do that
# this is the object as it is stored permanently
@dataclass
class FObSerialized:
    version: int
    ref_count: int
    fields: dict = field(default_factory = dict)


class FederatedObject:


    # there are some objects which do not exist in isolation.
    # they start with a reference count of zero.
    # In adelphos the only 1st class objects are the aliases.
    # every other object is dependent (in some way or another) with an alias.
    def __init__(self, uri, ref_count = 0, ob = None, locked = False):
        self.uri = uri
        # the object internally is a simple dict
        if ob is None:
            self.ob = FObSerialized(0, ref_count)
        else:
            self.ob = ob
        if locked:
            self.ts_locked = datetime.now() 
        else:
            self.ts_locked = False


    # gives a string representation of the object suitable to be
    # serialized to the store.
    def to_store_str(self):
        return json.dumps(asdict(self.ob))


    # Yuou can get a primitive value without locking.
    def get_primitive_value(self, key, maybe = False):
        return self.ob['fields'][key]


    # you cannot set a primitive value unless the object is locked.
    def set_primitive_value(self, key, val):
        if self.ts_locked is None:
            raise FdbException(EFdbErrors.EFDB_NO_LOCK_ON_OB)
        self.ob.fields[key] = val

