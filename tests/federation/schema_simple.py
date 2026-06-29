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


from app.federation.FederatedFactory import FederatedFactory
from app.federation.FederatedObject import FederatedObject
from app.federation.FederatedObject import FObColumnDefinition, FObColType, \
        FObCardType, FObReqType
from app.federation.FederatedUri import FederatedUri
from app.federation.FederatedFactory import FederatedFactoryRegistrar


TYPE_T1 = "TYPE_T1"
TYPE_T2 = "TYPE_T2"


class FederatedUriTest(FederatedUri):

    def unparse(self):
        base_name = "XX_test_type_" + self.ob_type + "/name=" + self.name
        if self.family is not None:
            base_name += f"/fam=_f{self.family}"
        if self.host is not None:
            base_name += f"_@f{self.host}"
        if self.fragment is not None:
            base_name += f"_#f{self.fragment}"
        return base_name


#class FedeObClass1(FederatedObject):
#
#    _schema = {
#            'key_int' : FObColumnDefinition(
#                FObColType.INTEGER,
#                FObCardType.SCALAR,
#                FObReqType.REQUIRED
#                ),
#            'key_str' : FObColumnDefinition(
#                FObColType.STRING,
#                FObCardType.SCALAR,
#                FObReqType.NO_REQUIRED_DEFAULT_NULL
#                )
#    }
#
#    def __init__(self, uri, ref_count, **kwargs):
#        super().__init__(uri, ref_count, **kwargs)
#
#
#    @classmethod
#    def get_schema(cls):
#        return cls._schema
#
#    
#    @classmethod
#    def register_class(cls):
#        reg = FederatedFactoryRegistrar(FedeObClass1, True, False)
#        FederatedFactory._register_ob_type(TYPE_T1, reg)
#
#
#class FedeObClass2(FederatedObject):
#
#
#    def __init__(self, uri, ref_count, **kwargs):
#        super().__init__(uri, ref_count, **kwargs)
#
#
#    @classmethod
#    def register_class(cls):
#        reg = FederatedFactoryRegistrar(FedeObClass2, False, False)
#        FederatedFactory._register_ob_type(TYPE_T2, reg)
#
#
#def my_test_schema_init():
#
#    FederatedFactory.set_uri_constructor(FederatedUriTest)
#
#    FedeObClass1.register_class()
#    FedeObClass2.register_class()
#

schema_simple_yaml = f"""

uri_constructor: 'tests.federation.schema_simple.FederatedUriTest'

classes:
    - uri_prefix: "{TYPE_T1}"
      first_class: true
      needs_family: false
      columns:
        - name: 'key_int'
          type: 'int'
          cardinality: 'scalar'
          required: true
        - name: 'key_str'
          type: 'str'
          cardinality: 'scalar'
          required: false

    - uri_prefix: "{TYPE_T2}"
      first_class: false
      needs_family: false
      columns: []

"""


LOCALHOST = "www.example.com"
OTHERHOST = "www.faraway.org"
LOCALHOST1 = "::1"
LOCALHOST2 = "localhost"
LOCALHOST3 = "127.0.0.1"


