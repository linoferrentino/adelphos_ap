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


# the base class that can create the objects in a federated store:

from app.federation.FdbException import FdbException
from app.federation.FdbException import EFdbErrors
from app.federation.FederatedObject import FObColumnDefinition, FObColType, \
        FObCardType, FObReqType
from dataclasses import dataclass
from dataclasses import field
import app.misc.utils as misc
from app.logging import gCon


@dataclass
class FederatedFactoryRegistrar:
    
    can_be_root : bool
    #needs_family : bool
    pars: dict = field(default_factory = dict)


class FederatedFactory:

    registrars = dict()
    uri_constructor = None

    
    @classmethod
    def set_uri_constructor(cls, uri_const):
        cls.uri_constructor = uri_const


    def __init__(self):
        self.registrars = dict()
        self.uri_constructor = None


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
            case _:
                raise Exception(f"Invalid col type {col_type_str}")


    @staticmethod
    def translate_cardinality(cardinality_str):
        match cardinality_str:
            case 'scalar':
                return FObCardType.SCALAR
            case _:
                raise Exception(f"Invalid cardinality {cardinality_str}")


    def _add_column(self, col, registrar):

        col_name = col['name']

        col_type_str = col['type']
        col_type_id = FederatedFactory.translate_type(col_type_str)
        cardinality_str = col['cardinality']
        cardinality_id = FederatedFactory.translate_cardinality(cardinality_str)
        required = col['required']
        def_value = None
        if required == False:
            def_value = col.get('default') 
            if def_value is None:
                required_type = FObReqType.NO_REQUIRED_DEFAULT_NULL
            else:
                required_type = FObReqType.NO_REQUIRED_DEFAULT_VALUE
        else:
            required_type = FObReqType.REQUIRED

        col_def = FObColumnDefinition(col_type_id, cardinality_id,
                                      required_type, def_value)

        registrar.pars[col_name] = col_def


    def _add_class(self, class_ob):
        uri_prefix = class_ob['uri_prefix']
        can_be_root = class_ob['can_be_root']
        registrar = FederatedFactoryRegistrar(can_be_root)

        col_array = class_ob ['columns']
        for col in col_array:
            self._add_column(col, registrar)

        self._register_ob_type(uri_prefix, registrar)


    def parse_schema(self, schema):

        uri_constructor_str = schema['uri_constructor']
        self.uri_constructor = misc.import_string(uri_constructor_str)

        classes_arr = schema['classes']
        for class_ob in classes_arr:
            self._add_class(class_ob)
            #gCon.log(f"I have added class {class_ob}")


    @classmethod
    def _register_ob_type(cls, type_str, registrar):
        cls.registrars[type_str] = registrar


    @classmethod
    def get_registrar(cls, uri_type):
        registrar = cls.registrars.get(uri_type)
        return registrar


