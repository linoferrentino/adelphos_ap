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


import re

from app.federation.FdbException import FdbException
from app.federation.FdbException import EFdbErrors
from app.federation.FederatedObject import FObColumnDefinition,\
        FObColType, FObCardType, FederatedEnum, FDB_RESERVED_PREFIX, \
        EUpgradeAction
from dataclasses import dataclass
from dataclasses import field
import app.misc.utils as misc
from app.logging import gCon
from enum import IntEnum

from app.misc.utils import import_string


   

@dataclass
class FederatedFactoryRegistrar:
    factory: object
    can_be_root : bool
    version: int
    pars: dict = field(default_factory = dict)
    upgrades: dict = field(default_factory = dict)


@dataclass
class FederatedFactoryUpgradeStep:
    action: EUpgradeAction
    old_name: str
    new_name: str
    default_value: str
    

class FederatedFactory:

    def __init__(self):
        self.reset()


    def reset(self):
        self.registrars = dict()
        self.uri_constructor = None
        self.enums = dict()


    @staticmethod
    def translate_type(col_type_str):
        match col_type_str:
            case 'int':
                return FObColType.INTEGER
            case 'str':
                return FObColType.STRING
            case 'real':
                return FObColType.REAL
            case 'local_uri':
                return FObColType.LOCAL_URI
            case 'json':
                return FObColType.JSON
            case 'enum':
                return FObColType.ENUM
            case 'uri':
                return FObColType.URI
            case _:
                raise Exception(f"Invalid col type {col_type_str}")


    @staticmethod
    def translate_cardinality(cardinality_str):
        match cardinality_str:
            case 'scalar':
                return FObCardType.SCALAR
            case 'array':
                return FObCardType.ARRAY
            case 'set':
                return FObCardType.SET
            case _:
                raise Exception(f"Invalid cardinality {cardinality_str}")


    def _get_subtype(self, col, col_type_id):
        if col_type_id != FObColType.ENUM:
            return None
        sub_type = col['sub_type']
        enum_val = self.enums[sub_type]
        return enum_val


    @staticmethod
    def _transform_age_str(age_str):
        unit_measure = age_str[-1]
        val = age_str[:-1]
        match unit_measure:
            case 'h' | 'H':
                return int(val) * 3600
            case 'd' | 'D':
                return int(val) * 86400
            case 's' | 'S':
                return int(val)
            case 'm' | 'M':
                return int(val) * 60
            case _:
                raise FdbException(EFdbErrors.EFDB_SCHEMA_SYNTAX_ERROR,
                        f"val {age_str} not understood")


    def _add_column(self, col, registrar):
        col_name = col['name']

        if re.match(FDB_RESERVED_PREFIX, col_name) is not None:
            raise FdbException(EFdbErrors.EFDB_RESERVED, col_name)

        if registrar.pars.get(col_name) is not None:
            raise FdbException(EFdbErrors.EFDB_DUPLICATED_COLUMN, col_name)

        col_type_str = col['type']
        col_type_id = FederatedFactory.translate_type(col_type_str)
        sub_type = self._get_subtype(col, col_type_id)
        cardinality_str = col['cardinality']
        cardinality_id = FederatedFactory.translate_cardinality(cardinality_str)
        transient_age_str = col.get('transient_age')
        transient_field = False
        def_value = None
        required = False
        read_only = False
        transient_age = None
        transient_hook = None

        if transient_age_str is not None:
            transient_field = True
            transient_func = col['transient_func']
            read_only = True
            transient_age = FederatedFactory._transform_age_str(
                    transient_age_str)
            transient_hook = import_string(transient_func)
        else:
            required = col.get('required', True)
            read_only = col.get('read_only', False)
            def_value = col.get('default') 

        minimum_cardinality = col.get('minimum_cardinality', 0)
        col_def = FObColumnDefinition(col_type_id, sub_type, cardinality_id,
              required, def_value, minimum_cardinality, read_only,
              transient_field, transient_hook, transient_age)
        #gCon.log(f"col {col_name} -> def {col_def}")
        registrar.pars[col_name] = col_def


    def _build_upgrades(self, upgrades, registrar):
        gCon.log(f"adding upgrade {upgrades}")
        list_upgrades = list()
        for upgrade_step in upgrades:
            old_name = None
            match upgrade_step['action']:
                case 'add_col':
                    action = EUpgradeAction.ADD_COLUMN
                    new_name = upgrade_step['name']
                    default_value = upgrade_step['default']
                case _:
                    raise Exception(f"todo {upgrade_step['action']}")
            upstep = FederatedFactoryUpgradeStep(action,
                            old_name, new_name, default_value)
            list_upgrades.append(upstep)
        return list_upgrades


    def _add_class(self, class_ob):
        uri_prefix = class_ob['uri_prefix']
        can_be_root = class_ob['can_be_root']
        version = class_ob['version']
        registrar = FederatedFactoryRegistrar(self, can_be_root, version)

        col_array = class_ob ['columns']
        for col in col_array:
            self._add_column(col, registrar)

        upgrades = class_ob.get('schema_upgrades')
        if upgrades is not None:
            for upgrade, upgrade_def in upgrades.items():
                upgrade_steps = self._build_upgrades(upgrade_def, registrar)
                registrar.upgrades[upgrade] = upgrade_steps

        self._register_ob_type(uri_prefix, registrar)


    def _add_enums(self, enums):
        for enum, fields in enums.items():
            this_enum = FederatedEnum(fields)
            self.enums[enum] = this_enum


    def _add_types(self, types):
        enums = types.get('enums')
        self._add_enums(enums)


    def parse_schema(self, fdb, schema):
        self.fdb = fdb
        uri_constructor_str = schema['uri_constructor']
        self.uri_constructor = misc.import_string(uri_constructor_str)

        types = schema.get('types')
        if types is not None:
            self._add_types(types)

        classes_arr = schema['classes']
        for class_ob in classes_arr:
            self._add_class(class_ob)


    def _register_ob_type(self, type_str, registrar):
        if self.registrars.get(type_str) is not None:
            raise FdbException(EFdbErrors.EFDB_DUPLICATED_CLASS, type_str)
        self.registrars[type_str] = registrar


    def get_registrar(self, uri_type):
        registrar = self.registrars.get(uri_type)
        return registrar


