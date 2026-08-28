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

from abc import ABC
from abc import abstractmethod

from collections.abc import Iterable

import copy
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


def str_to_fobs(str_ob):
    ob = json.loads(str_ob)
    obs = FObSerialized(**ob)
    return obs


def str_to_fob(uri_ob, registrar, str_ob, locked = False):
    obs = str_to_fobs(str_ob)
    fob = FederatedObject(uri_ob, registrar, ob = obs, locked = locked)
    return fob


def ensure_lock(func):

    def _locked_or_croak(self, *args, **kwargs):
        if ((self.ts_locked is False) and (self.ob.state != EObState.DETACHED)):
            raise FdbException(EFdbErrors.EFDB_NO_LOCK_ON_OB)
        return func(self, *args, **kwargs)

    return _locked_or_croak


def enforce_schema_scalar(func):
    def _inner_enforce(self, key, val, *args):
        schema = self.registrar.pars
        par = schema.get(key)
        if par is None:
            raise FdbException(EFdbErrors.EFDB_UNKNOWN_COLUMN, key)
        if par.cardinality != FObCardType.SCALAR:
            raise FdbException(EFdbErrors.EFDB_SCALAR_EXPECTED, key)

        FederatedObject.enforce_scalar(key, val, par, False)

        return func(self, key, val, *args)

    return _inner_enforce


def enforce_uri_type(func):
    def _inner_enforce(self, key, *args):
        schema = self.registrar.pars
        par = schema.get(key)
        if (par.typecol != FObColType.URI and 
            par.typecol != FObColType.LOCAL_URI):
            raise FdbException(EFdbErrors.EFDB_URI_EXPECTED, key)
        return func(self, key, *args)

    return _inner_enforce



def enforce_schema_not_scalar_scalar(func):
    def _inner_enforce(self, key, val, *args):
        schema = self.registrar.pars
        par = schema.get(key)
        if par is None:
            raise FdbException(EFdbErrors.EFDB_UNKNOWN_COLUMN, key)
        if par.cardinality == FObCardType.SCALAR:
            raise FdbException(EFdbErrors.EFDB_SCALAR_UNEXPECTED, key)

        FederatedObject.enforce_scalar(key, val, par, False)

        return func(self, key, val, *args)

    return _inner_enforce


def enforce_schema_not_scalar_not_scalar(func):
    def _inner_enforce(self, key, val, *args):
        schema = self.registrar.pars
        par = schema.get(key)
        if par is None:
            raise FdbException(EFdbErrors.EFDB_UNKNOWN_COLUMN, key)
        if par.cardinality == FObCardType.SCALAR:
            raise FdbException(EFdbErrors.EFDB_SCALAR_UNEXPECTED, key)

        for val_item in val:
            FederatedObject.enforce_scalar(key, val_item, par, False)

        return func(self, key, val, *args)

    return _inner_enforce



def enforce_schema_scalar_read(func):
    def _inner_enforce(self, key, *args):
        schema = self.registrar.pars
        par = schema.get(key)
        if par is None:
            raise FdbException(EFdbErrors.EFDB_UNKNOWN_COLUMN, key)
        if par.cardinality != FObCardType.SCALAR:
            raise FdbException(EFdbErrors.EFDB_SCALAR_EXPECTED, key)

        return func(self, key, *args)

    return _inner_enforce



def enforce_schema_not_scalar_read(func):
    def _inner_enforce(self, key, *args):
        schema = self.registrar.pars
        par = schema.get(key)
        if par is None:
            raise FdbException(EFdbErrors.EFDB_UNKNOWN_COLUMN, key)
        if par.cardinality == FObCardType.SCALAR:
            raise FdbException(EFdbErrors.EFDB_SCALAR_UNEXPECTED, key)

        return func(self, key, *args)

    return _inner_enforce


def enforce_set(func):
    def _inner_enforce(self, key, *args):
        schema = self.registrar.pars
        par = schema.get(key)
        if par.cardinality != FObCardType.SET:
            raise FdbException(EFdbErrors.EFDB_SET_EXPECTED, key)

        return func(self, key, *args)

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


class EObState(IntEnum):
    PRESENT = 0
    LENT = 1
    BORROWED = 2
    CLONED = 3
    DETACHED = 4


FDB_RESERVED_PREFIX = "_fdb_"

REF_COUNT_COLUMN = f"{FDB_RESERVED_PREFIX}ref_count"
VERSION_COLUMN   = f"{FDB_RESERVED_PREFIX}version"


@dataclass
class FObSerialized:
    state: EObState
    fields: dict = field(default_factory = dict)

    @property
    def ref_count(self):
        return self.fields[REF_COUNT_COLUMN]


    @property
    def version(self):
        return self.fields[VERSION_COLUMN]


    @property
    def get_state(self):
        return self.state


class FObColType(IntEnum):

    INTEGER = 0
    STRING = 1
    REAL = 2
    DATETIME = 3
    BOOL = 4
    URI = 5
    LOCAL_URI = 6
    JSON = 7
    ENUM = 8


class FObCardType(IntEnum):

    SCALAR = 0
    ARRAY = 1
    SET = 2


class FederatedType(ABC):

    @abstractmethod
    def enforce_type(self, value, before_commit):
        pass


class FederatedEnum(FederatedType):

    def __init__(self, items):
        self.items = set(items)


    def enforce_type(self, value, before_commit):
        if value not in self.items:
            raise FdbException(EFdbErrors.EFDB_INVALID_ENUM_VALUE, value)
        return value


@dataclass
class FObColumnDefinition:

    typecol : FObColType
    sub_type : object
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

            self.ob = FObSerialized(EObState.PRESENT)
            self.ob.fields[REF_COUNT_COLUMN] = ref_count
            self.ob.fields[VERSION_COLUMN] = 0
            self._enforce_schema_init(fields)
            self.modified = True
        else:
            self.ob = ob
            self.modified = False

        if locked:
            self.ts_locked = True 
        else:
            assert ob is not None
            self.ts_locked = False


    def enforce_lock(self):
        if self.ts_locked is False:
            raise FdbException(EFdbErrors.EFDB_NO_LOCK_ON_OB)
 

    @staticmethod
    def enforce_def(col_name, col_val, col_def, before_commit = False):
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
                #gCon.log(f"col_val {col_val} is {type(col_val)}")
                raise FdbException(EFdbErrors.EFDB_ITEARABLE_EXPECTED, col_val)

            if col_def.minimum_cardinality is not None:
                if len(col_val) < col_def.minimum_cardinality:
                    raise FdbException(EFdbErrors.EFDB_CARDINALITY_LOWER,
           f"{col_name} len {len(col_val)} < {col_def.minimum_cardinality}")

            for val in col_val:
                FederatedObject.enforce_scalar(col_name, val, col_def, before_commit)


    @staticmethod
    def _enforce_enum_value(col_name, col_val, col_def, before_commit):
        pass


    def returned_object(self, obstr):
        gCon.log(f"[green]Object {self.uri.unparse()} returned[/green]")
        ob = json.loads(obstr)
        obs = FObSerialized(**ob)
        self.ob = obs
        self.ob.state = EObState.PRESENT
        self.modified = True


    def lent_to(self, social_handle):
        gCon.log(f"[red]Object {self.uri.unparse()} lent to {social_handle}[/red]")
        now = datetime.now()
        now_str = now.strftime("%Y-%m-%dT%H:%M:%S.%f")
        self.ob.state = EObState.LENT
        backup_fields = self.ob.fields
        self.ob.fields = {
            'lent_to' : social_handle,
            'date_lending' : now_str,
            'backup' : backup_fields
        }
        self.modified = True


    @staticmethod
    def enforce_scalar(col_name, col_val, col_def, before_commit):
        if col_val is None:
            if before_commit == True:
                if col_def.required:
                    gCon.log(f"The col_def for {col_name} is {col_def}")
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
            case FObColType.ENUM:
                exp_type = str
            case _:
                raise FdbException(EFdbErrors.EFDB_INVALID_VAL_TYPE, col_name)

        if isinstance(col_val, exp_type) == False:
            raise FdbException(EFdbErrors.EFDB_INVALID_VAL_TYPE, 
            f"exp {exp_type} found {type(col_val)} in {col_name}")

        match col_type:
            case FObColType.ENUM:
                col_def.sub_type.enforce_type(col_val, before_commit)


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


    @enforce_schema_scalar_read
    def get_scalar(self, key, maybe = False):
        if maybe == False:
            return self.ob.fields[key]
        val = self.ob.fields.get(key)
        if val is not None:
            return val
        if maybe == True:
            return None
        raise AttributeError(key)


    def detach(self):
        if self.modified == True:
            raise FdbException(EFdbErrors.EFDB_CANNOT_DETACH_A_MODIFIED_OBJECT)
        if self.ts_locked == True:
            raise FdbException(EFdbErrors.EFDB_CANNOT_DETACH_A_LOCKED_OBJECT)

        detached_ob = copy.deepcopy(self.ob)
        detached_ob.state = EObState.DETACHED
        detached = FederatedObject(self.uri, self.registrar,
                                   ob = detached_ob)
        return detached


    def add_ref(self):
        self._inc_ref_ob()

    @ensure_lock
    @enforce_schema
    def set_link(self, key, new_ob):
        self._compare_and_swap_link_impl(key, None, new_ob)


    @enforce_set
    def get_set(self, key):
        cur_value = self.ob.fields[key]
        gCon.log(f"get_set {key} return {cur_value}")
        return set(cur_value)


    @enforce_set
    @ensure_lock
    def remove_set(self, key, ob):
        ob().enforce_lock()
        schema = self.registrar.pars
        par = schema.get(key)
        cur_value = self.ob.fields[key]
        gCon.log(f"cur_value {key} {cur_value}")
        if cur_value is None:
            raise FdbException(EFdbErrors.EFDB_VALUE_NOT_PRESENT, key)
        uri_str = ob().uri.unparse(par.typecol == FObColType.LOCAL_URI)
        uri_set = set(cur_value)
        if uri_str not in uri_set:
            raise FdbException(EFdbErrors.EFDB_VALUE_NOT_PRESENT, key)
        uri_set.remove(uri_str)
        uri_list = list(uri_set)
        gCon.log(f"new value {uri_list}")
        self.ob.fields[key] = uri_list
        ob()._dec_ref_ob()
        self.modified = True
        

    @enforce_schema_not_scalar_read
    def get_as_list(self, key):
        cur_value = self.ob.fields.get(key)
        if cur_value is None:
            return []
        return list(cur_value)
                

    @ensure_lock
    @enforce_schema_not_scalar_not_scalar
    def set_list(self, key, new_list):
        self.ob.fields[key] = copy.deepcopy(new_list)
        self.modified = True


    @ensure_lock
    @enforce_schema_not_scalar_scalar
    @enforce_uri_type
    def add_link(self, key, ob):
        schema = self.registrar.pars
        par = schema.get(key)
        cur_value = self.ob.fields[key]

        uri_str = ob().uri.unparse(par.typecol == FObColType.LOCAL_URI)

        if par.cardinality == FObCardType.SET:
            if cur_value is None:
                cur_set = { uri_str }
                ob()._inc_ref_ob()
            else:
                cur_set = set(cur_value)
                if uri_str in cur_set:
                    return
                else:
                    cur_set.add(uri_str)
                    ob()._inc_ref_ob()
            self.ob.fields[key] = list(cur_set)
            self.modified = True

        elif par.cardinality == FObCardType.ARRAY:
            raise Exception("TO DO")

        else:
            raise Exception("TO DO 1")


    def downvote_uri(self, uri_to_downvote, tx_ob):
        gCon.log(f"need to downvote the URI {uri_to_downvote}")
        ob_to_downvote = tx_ob.downvote_deleted_ob(uri_to_downvote)


    def prepare_to_oblivion(self, tx_ob):
        if hasattr(self, 'prepared_to_oblivion'):
            return 
        gCon.log("[red]prepare to oblivion[/red]")
        for par, definition in self.registrar.pars.items():
            if ((definition.typecol != FObColType.URI)
                and (definition.typecol != FObColType.LOCAL_URI)):
                    continue
            uris_to_downvote = self.ob.fields[par] 
            if definition.cardinality == FObCardType.SCALAR:
                if uris_to_downvote is not None:
                    self.downvote_uri(uris_to_downvote, tx_ob)
            elif definition.cardinality == FObCardType.SET:
                set_uri_downvoted = set(uris_to_downvote)
                for uri_to_downvote in set_uri_downvoted:
                    self.downvote_uri(uri_to_downvote, tx_ob)
            else:
                raise Exception("To do")
        self.prepared_to_oblivion = True


    @ensure_lock
    @enforce_schema
    def compare_and_swap_link(self, key, expected_ob, new_ob):
        self._compare_and_swap_link_impl(key, expected_ob, new_ob)
        

    def _compare_and_swap_link_impl(self, key, expected_ob, new_ob):
        schema = self.registrar.pars
        par = schema.get(key)

        prev_link = self.ob.fields.get(key)

        if expected_ob is None:
            exp_link = None
        else:
            exp_link = expected_ob().uri.unparse(
                par.typecol == FObColType.LOCAL_URI)

        if prev_link != exp_link:
            raise FederatedObject(EFdbErrors.EFDB_URI_NOT_EXPECTED, prev_link)

        if new_ob is None:
            new_link = None
        else:
            new_link = new_ob().uri.unparse(
                par.typecol == FObColType.LOCAL_URI)
       
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
        assert self.ob.fields[REF_COUNT_COLUMN] > 0
        self.ob.fields[REF_COUNT_COLUMN] -= 1
        self.modified = True


    @ensure_lock
    def _inc_ref_ob(self):
        assert self.ob.fields[REF_COUNT_COLUMN] >= 0
        self.ob.fields[REF_COUNT_COLUMN] += 1
        self.modified = True


    @property
    def ref_count(self):
        return self.ob.fields[REF_COUNT_COLUMN]


    @property
    def version(self):
        return self.ob.fields[VERSION_COLUMN]


    @ensure_lock
    @enforce_schema
    def set_scalar(self, key, val):
        if self.ob.fields.get(key) != val:
            self.ob.fields[key] = copy.deepcopy(val)
            self.modified = True


    @ensure_lock
    @enforce_schema_not_scalar_scalar
    def add_scalar(self, key, val):
        schema = self.registrar.pars
        par = schema.get(key)
        cur_value = self.ob.fields[key]

        if par.cardinality == FObCardType.ARRAY:

            if cur_value is None:
                cur_value = [ copy.deepcopy(val) ]
            else:
                cur_value.append(copy.deepcopy(val))

            self.ob.fields[key] = cur_value
            self.modified = True
            
        else:

            raise Exception(f"to do {key} {par}")
