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


def ensure_val_type(atype):
    def ensure_this_type(func):
        def is_val_type_or_die(self, key, val):
            if isinstance(val, atype) == False:
                raise FdbException(EFdbErrors.EFDB_INVALID_VAL_TYPE)
            return func(self, key, val)
        return is_val_type_or_die
    return ensure_this_type


def enforce_schema(func):
    def _inner_enforce(self, key, val):
        schema = self.registrar.pars
        par = schema.get(key)
        if par is None:
            raise FdbException(EFdbErrors.EFDB_UNKNOWN_COLUMN, key)
        if par.cardinality != FObCardType.SCALAR:
            raise FdbException(EFdbErrors.EFDB_SCALAR_NOT_EXPECTED, key)
        gCon.log(f"enforcing {par}")
        return func(self, key, val)

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
    LIST = 2
    STACK = 3


class FObReqType(IntEnum):

    REQUIRED = 0
    NO_REQUIRED_DEFAULT_NULL = 1
    NO_REQUIRED_DEFAULT_VALUE = 2


@dataclass
class FObColumnDefinition:

    typecol : FObColType
    cardinality : FObCardType
    required : FObReqType = FObReqType.NO_REQUIRED_DEFAULT_NULL
    default_value : object = None


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
    def _enforce_type(col_val, col_type):
        match col_type:
            case FObColType.INTEGER:
                exp_type = int
            case FObColType.STRING:
                exp_type = str
            case FObColType.REAL:
                exp_type = float
            case FObColType.BOOL:
                exp_type = bool
            case _:
                exp_type = None

        if exp_type is not None:
            if isinstance(col_val, exp_type) == False:
                raise FdbException(EFdbErrors.INVALID_COLUMN_TYPE, 
                f"exp {exp_type} found {type(col_val)}")
            return col_val

        assert col_type == FObColType.DATETIME


    @staticmethod
    def _enforce_not_uri(cold_def):
        if cold_def != FObColType.URI:
            return
        raise FdbException(EFdbErrors.EFDB_URIS_MUST_BE_NULLS)


    def _enforce_schema_init(self, fields):

        schema = self.registrar.pars

        for field in fields.keys():
            if field not in schema:
                raise FdbException(EFdbErrors.EFDB_EXTRA_FIELD, field)

        for col_name, col_def in schema.items():

            if col_def.cardinality != FObCardType.SCALAR:
                self.ob.fields[col_name] = []
                continue

            col_val = None
            match col_def.required:
                case FObReqType.REQUIRED:
                    FederatedObject._enforce_not_uri(col_def.typecol)
                    col_val = fields.get(col_name)
                    if col_val is None:
                        raise FdbException(EFdbErrors.EFDB_REQUIRED_FIELD_MISSING, col_name) 
                    col_val = FederatedObject._enforce_type(col_val, col_def.typecol)
                case FObReqType.NO_REQUIRED_DEFAULT_NULL:
                    pass
                case FObReqType.NO_REQUIRED_DEFAULT_VALUE:
                    FederatedObject._enforce_not_uri(col_def.typecol)
                    col_val = col_def.default_value
            self.ob.fields[col_name] = col_val

    
    def to_store_str(self):
        store_str = json.dumps(asdict(self.ob))
        return store_str


    def get_primitive_value(self, key, maybe = False):
        return self.ob.fields[key]


    def val(self, key, maybe = False):
        if maybe == False:
            return self.ob.fields[key]
        val = self.ob.fields.get(key)
        if val is not None:
            return val
        if maybe == True:
            return None
        raise AttributeError(key)


    def get_link(self, key):
        prev_link = self.ob.fields.get(key)


    def add_phantom_link(self):
        self._inc_ref_ob()


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
        self.modified = True


    @ensure_lock
    def _inc_ref_ob(self):
        # 0 is valid, it might be created in this transaction.
        assert self.ob.ref_count >= 0
        self.ob.ref_count += 1
        self.modified = True


    @ensure_lock
    @ensure_val_type(str)
    @enforce_schema
    def set_primitive_value(self, key, val):
        if self.ob.fields.get(key) != val:
            self.ob.fields[key] = val
            self.modified = True


