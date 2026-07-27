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


from app.federation.FdbException import FdbException
from app.federation.FdbException import EFdbErrors
from app.federation.FederatedObject import FObColumnDefinition,\
        FObColType, FObCardType, FederatedEnum
from dataclasses import dataclass
from dataclasses import field
import app.misc.utils as misc
from app.logging import gCon


@dataclass
class FederatedFactoryRegistrar:
    
    can_be_root : bool
    pars: dict = field(default_factory = dict)


class FederatedFactory:

    def __init__(self):
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


    def _add_column(self, col, registrar):
        col_name = col['name']

        col_type_str = col['type']
        col_type_id = FederatedFactory.translate_type(col_type_str)
        sub_type = self._get_subtype(col, col_type_id)
        cardinality_str = col['cardinality']
        cardinality_id = FederatedFactory.translate_cardinality(cardinality_str)
        required = col.get('required', True)
        def_value = col.get('default') 
        minimum_cardinality = col.get('minimum_cardinality', 0)
        col_def = FObColumnDefinition(col_type_id, sub_type, cardinality_id,
                                      required, def_value, minimum_cardinality)
        registrar.pars[col_name] = col_def


    def _add_class(self, class_ob):
        uri_prefix = class_ob['uri_prefix']
        can_be_root = class_ob['can_be_root']
        registrar = FederatedFactoryRegistrar(can_be_root)

        col_array = class_ob ['columns']
        for col in col_array:
            self._add_column(col, registrar)

        self._register_ob_type(uri_prefix, registrar)


    def _add_enums(self, enums):
        for enum, fields in enums.items():
            this_enum = FederatedEnum(fields)
            self.enums[enum] = this_enum


    def _add_types(self, types):
        enums = types.get('enums')
        self._add_enums(enums)


    def parse_schema(self, schema):
        uri_constructor_str = schema['uri_constructor']
        self.uri_constructor = misc.import_string(uri_constructor_str)

        types = schema.get('types')
        if types is not None:
            self._add_types(types)

        classes_arr = schema['classes']
        for class_ob in classes_arr:
            self._add_class(class_ob)


    def _register_ob_type(self, type_str, registrar):
        self.registrars[type_str] = registrar


    def get_registrar(self, uri_type):
        registrar = self.registrars.get(uri_type)
        return registrar


