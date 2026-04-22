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
from enum import IntEnum

from app.federation.FdbException import FdbException
from app.federation.FdbException import EFdbErrors

# this is the basic class that holds a federated object,
# the federated db is responsible for its life cycle

# a federated object is an object which is identified by a federated uri.


# the federated object can be built from a string and serialize itself
# to a string: 


def str_to_fob(uri_ob, str_ob, locked = False):
    ob = json.loads(str_ob)
    obs = FObSerialized(**ob)
    fob = FederatedObject(uri_ob, ob = obs, locked = locked)
    return fob


def ensure_lock(func):

    def _locked_or_croak(self, *args, **kwargs):
        if self.ts_locked is None:
            raise FdbException(EFdbErrors.EFDB_NO_LOCK_ON_OB)
        return func(self, *args, **kwargs)

    return _locked_or_croak


def ensure_val_type(atype):
    def ensure_this_type(func):
        def is_val_type_or_die(self, key, val):
            if isinstance(val, atype) == False:
                raise FdbException(EFdbErrors.EFDB_INVALID_VAL_TYPE)
            return func(self, key, val)
        return is_val_type_or_die
    return ensure_this_type

#want_val_FederatedObject = ensure_val_type(FederatedObject)


# the schema is free: we do not enforce a schema, derived classes should do that
# this is the object as it is stored permanently
@dataclass
class FObSerialized:
    version: int
    ref_count: int
    fields: dict = field(default_factory = dict)


class FederatedColumnType(IntEnum):

    INTEGER = 0
    STRING = 1
    REAL = 2
    DATETIME = 3
    BOOL = 4
    URI = 5
    ARRAY = 6


class FederatedObSchemaTbl(dict):

    pass



class FederatedObject:


    # there are some objects which do not exist in isolation.
    # they start with a reference count of zero.
    # In adelphos the only 1st class objects are the aliases.
    # every other object is dependent (in some way or another) with an alias.
    def __init__(self, uri, ref_count = 0, ob = None, locked = False):
        self.uri = uri
        self.modified = False

        if ob is None:
            self.ob = FObSerialized(0, ref_count)
        else:
            self.ob = ob

        if locked:
            self.ts_locked = datetime.now() 
        else:
            self.ts_locked = False

    
    def to_store_str(self):
        return json.dumps(asdict(self.ob))


    def get_primitive_value(self, key, maybe = False):
        return self.ob.fields[key]


    def get_link(self, key):
        prev_link = self.ob.fields.get(key)


    @ensure_lock
    def compare_and_swap_link(self, key, expected_ob, new_ob):

        prev_link = self.ob.fields.get(key)

        if expected_ob is None:
            exp_link = None
        else:
            exp_link = expected_ob().uri.unparse()

        if prev_link != exp_link:
            return

        if new_ob is None:
            new_link = None
        else:
            new_link = new_ob().uri.unparse()
       
        if prev_link == new_link:
            return

        if expected_ob is not None:
            expected_ob()._dec_ref_ob()

        if new_ob is not None:
            new_ob()._inc_ref_ob()

        self.ob.fields[key] = new_link
        self.modified = True


    @ensure_lock
    def _dec_ref_ob(self):
        assert self.ob.ref_count > 0
        self.ob.ref_count -= 1
        gCon.log(f"{self.uri} DEC new ref count {self.ob.ref_count}")
        self.modified = True


    @ensure_lock
    def _inc_ref_ob(self):
        # 0 is valid, it might be created in this transaction.
        assert self.ob.ref_count >= 0
        self.ob.ref_count += 1
        gCon.log(f"{self.uri} INC new ref count {self.ob.ref_count}")
        self.modified = True


    @ensure_lock
    @ensure_val_type(str)
    def set_primitive_value(self, key, val):
        if self.ob.fields.get(key) != val:
            self.ob.fields[key] = val
            self.modified = True


