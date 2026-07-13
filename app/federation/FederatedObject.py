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


import json
import dataclasses

from enum import IntEnum
from dataclasses import dataclass
from dataclasses import asdict
from dataclasses import field
from datetime import datetime

from app.logging import gCon
from app.federation.FdbException import FdbException
from app.federation.FdbException import EFdbErrors

import weakref


def str_to_fob(uri_ob, registrar, str_ob, locked = False):
    ob = json.loads(str_ob)
    obs = FObSerialized(**ob)
    fob = FederatedObject(uri_ob, registrar, ob = obs, locked = locked)
    return fob


def ensure_lock(func):

    def _locked_or_croak(self, *args, **kwargs):
        if self.ts_locked is None:
            raise FdbException(EFdbErrors.EFDB_NO_LOCK_ON_OB)
        return func(self, *args, **kwargs)

    return _locked_or_croak


def enforce_schema_not_scalar(func):
    def _inner_enforce(self, key, val, *args):
        schema = self.registrar.pars
        par = schema.get(key)
        if par.cardinality == FObCardType.SCALAR:
            raise FdbException(EFdbErrors.EFDB_SCALAR_EXPECTED, key)

        return func(self, key, val, *args)

    return _inner_enforce



def enforce_schema(func):
    def _inner_enforce(self, key, val, *args):
        schema = self.registrar.pars
        par = schema.get(key)
        if par is None:
            raise FdbException(EFdbErrors.EFDB_UNKNOWN_COLUMN, key)
        if par.cardinality != FObCardType.SCALAR:
            raise FdbException(EFdbErrors.EFDB_SCALAR_UNEXPECTED, key)

        FederatedObject.enforce_scalar(key, val, par, False)

        return func(self, key, val, *args)

    return _inner_enforce


@dataclass
class FObSerialized:
    version: int
    ref_count: int
    fields: dict = field(default_factory = dict)


class FObColType(IntEnum):

    INTEGER = 0
    STRING = 1
    REAL = 2
    DATETIME = 3
    BOOL = 4
    URI = 5
    LOCAL_URI = 6
    JSON = 7


class FObCardType(IntEnum):

    SCALAR = 0
    ARRAY = 1
    SET = 2
    #LIST = 2
    #STACK = 3


#class FObReqType(IntEnum):
#
#    REQUIRED = 0
#    NO_REQUIRED_DEFAULT_NULL = 1
#    NO_REQUIRED_DEFAULT_VALUE = 2


@dataclass
class FObColumnDefinition:

    typecol : FObColType
    cardinality : FObCardType
    required : bool
    default_value : object
    minimum_cardinality: int


class FederatedObject:

    def __init__(self, uri, registrar, *, ob = None, locked = False, 
                 fields = {}):
        self.uri = uri

        self.registrar = registrar

        if ob is None:
            if registrar.can_be_root:
                ref_count = 1
            else:
                ref_count = 0

            self.ob = FObSerialized(0, ref_count)
            self._enforce_schema_init(fields)
            self.modified = True
        else:
            self.ob = ob
            self.modified = False

        if locked:
            self.ts_locked = datetime.now() 
        else:
            assert ob is not None
            self.ts_locked = None


    @staticmethod
    def enforce_def(col_name, col_val, col_def, before_commit = False):
        gCon.log(f"enforcing {col_name} value {col_val} with {col_def} commit {before_commit}")
        if col_def.cardinality == FObCardType.SCALAR:
            FederatedObject.enforce_scalar(col_name, col_val, col_def, before_commit)
        else:

            if col_val is None:
                if before_commit == False:
                    return
                elif col_def.required == True:
                    raise FdbException(EFdbErrors.EFDB_REQUIRED_FIELD_MISSING,
                                    col_name)
                else:
                    return
               
            if isinstance(col_val, list) == False:
                gCon.log(f"col_val {col_val} is {type(col_val)}")
                raise FdbException(EFdbErrors.EFDB_ITEARABLE_EXPECTED, col_val)

            for val in col_val:
                FederatedObject.enforce_scalar(col_name, val, col_def, before_commit)


    @staticmethod
    def enforce_scalar(col_name, col_val, col_def, before_commit):

        if col_val is None:
            if before_commit == True:
                if col_def.required:
                    raise FdbException(EFdbErrors.EFDB_REQUIRED_FIELD_MISSING,
                                       col_name)
            return

        col_type = col_def.typecol
        match col_type:
            case FObColType.DATETIME:
                exp_type = datetime
            case FObColType.JSON:
                exp_type = dict
            case FObColType.INTEGER:
                exp_type = int
            case FObColType.STRING:
                exp_type = str
            case FObColType.REAL:
                exp_type = float
            case FObColType.BOOL:
                exp_type = bool
            case FObColType.LOCAL_URI | FObColType.URI:
                if before_commit == True:
                    exp_type = str
                else:
                    exp_type = weakref.ReferenceType
            case _:
                raise FdbException(EFdbErrors.EFDB_INVALID_VAL_TYPE)

        if isinstance(col_val, exp_type) == False:
            raise FdbException(EFdbErrors.EFDB_INVALID_VAL_TYPE, 
            f"exp {exp_type} found {type(col_val)} in {col_name}")



    @staticmethod
    def _enforce_not_uri(col_name, col_def):
        if ((col_def == FObColType.URI) or (col_def == FObColType.LOCAL_URI)):
            raise FdbException(EFdbErrors.EFDB_URIS_CANNOT_BE_SET_DIRECTLY, col_name)


    @staticmethod
    def is_uri(col_def):
        if ((col_def == FObColType.URI) or (col_def == FObColType.LOCAL_URI)):
            return True
        return False


    def enforce_schema_before_commit(self):
        schema = self.registrar.pars
        for col_name, col_def in schema.items():
            col_field = self.ob.fields.get(col_name)
            FederatedObject.enforce_def(col_name, col_field, col_def, True)


    def _enforce_schema_init(self, fields):

        schema = self.registrar.pars

        for field in fields.keys():
            if field not in schema:
                raise FdbException(EFdbErrors.EFDB_EXTRA_FIELD, field)

        for col_name, col_def in schema.items():

            col_field = fields.get(col_name)
            if col_def.required:
                
                if col_field is None:
                    if FederatedObject.is_uri(col_def.typecol) == False:
                        raise FdbException(EFdbErrors.EFDB_REQUIRED_FIELD_MISSING,
                                       col_name) 
                else:
                    FederatedObject._enforce_not_uri(col_name, col_def.typecol)
                    FederatedObject.enforce_def(col_name, col_field, col_def)
                col_val = col_field

            else:
                if col_field is not None:
                    FederatedObject._enforce_not_uri(col_name, col_def.typecol)
                    col_val = col_field
                else:
                    col_val = col_def.default_value 

            self.ob.fields[col_name] = col_val

    
    def to_store_str(self):
        store_str = json.dumps(asdict(self.ob))
        return store_str


    def get_scalar(self, key, maybe = False):
        if maybe == False:
            return self.ob.fields[key]
        val = self.ob.fields.get(key)
        if val is not None:
            return val
        if maybe == True:
            return None
        raise AttributeError(key)


    def add_phantom_link(self):
        self._inc_ref_ob()


    @ensure_lock
    @enforce_schema
    def set_link(self, key, new_ob):
        self._compare_and_swap_link_impl(key, None, new_ob)


    @ensure_lock
    @enforce_schema_not_scalar
    def add_link(self, key, ob):
        schema = self.registrar.pars
        par = schema.get(key)
        cur_value = self.ob.fields[key]
        if par.cardinality == FObCardType.SET:
            if cur_value is None:
                cur_set = { ob().uri.unparse() }
            else:
                cur_set = set(cur_value)
                cur_set.add(ob.uri.unparse())
            self.ob.fields[key] = list(cur_set)
        elif par.cardinality == FObCardType.ARRAY:
            raise Exception("TO DO")
        else:
            raise Exception("TO DO 1")


    @ensure_lock
    @enforce_schema
    def compare_and_swap_link(self, key, expected_ob, new_ob):
        self._compare_and_swap_link_impl(key, expected_ob, new_ob)
        

    def _compare_and_swap_link_impl(self, key, expected_ob, new_ob):
        prev_link = self.ob.fields.get(key)

        if expected_ob is None:
            exp_link = None
        else:
            exp_link = expected_ob().uri.unparse()

        if prev_link != exp_link:
            raise FederatedObject(EFdbErrors.EFDB_URI_NOT_EXPECTED, prev_link)

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
        self.modified = True


    @ensure_lock
    def _inc_ref_ob(self):
        assert self.ob.ref_count >= 0
        self.ob.ref_count += 1
        self.modified = True


    @ensure_lock
    @enforce_schema
    def set_scalar(self, key, val):
        if self.ob.fields.get(key) != val:
            self.ob.fields[key] = val
            self.modified = True


