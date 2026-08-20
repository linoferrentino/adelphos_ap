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

from app.federation.FederatedFactory import FederatedFactory
from app.federation.FederatedObject import FederatedObject
from app.federation.FederatedObject import FObColumnDefinition, FObColType, FObCardType 
from app.federation.FederatedUri import FederatedUri
from app.federation.FederatedFactory import FederatedFactoryRegistrar

from app.exc.AdelphosException import AdelphosException
from app.exc.AdelphosException import AdErrno

TYPE_T1 = "TYPE_T1"
TYPE_T2 = "TYPE_T2"


class FederatedUriTest(FederatedUri):

    def unparse(self, force_local = False):
        base_name = "XX_test_type_" + self.ob_type + "/name=" + self.name
        if self.fragment is not None:
            base_name += f"#{self.fragment}"
        if force_local == False:
            base_name += self._base_get_host_part()
        return base_name


    @staticmethod
    def create_uri(uri_type, object_part, *, host_part = None, fragment = None):
        uri = FederatedUriTest(uri_type, object_part, host = host_part,
                               fragment = fragment)
        return uri


    @classmethod
    def divide_type_name(cls, object_part):
        type_name_match = re.match(
r"XX_test_type_(\w*?)/name=(\w*)$", object_part)

        if (type_name_match is None):
            raise AdelphosException(AdErrno.EINVALID_URI, 
f"Illegal URI {object_part} I was expecting something like #<type>#<name>")

        uri_type = type_name_match.group(1)
        name_part= type_name_match.group(2)

        return (uri_type, name_part)


schema_reserved_error = f"""

uri_constructor: 'tests.federation.schema_simple.FederatedUriTest'

types:


classes:
    - uri_prefix: err_prefix
      can_be_root: true 
      columns:
        - name: _fdb_impossible
          type: int
          cardinality: scalar
          required: true

"""
  
schema_duplicated_class = f"""

uri_constructor: 'tests.federation.schema_simple.FederatedUriTest'

types:


classes:

    - uri_prefix: cloned_error
      can_be_root: true 
      columns:
        - name: age 
          type: int
          cardinality: scalar
          required: true

    - uri_prefix: cloned_error
      can_be_root: true 
      columns:
        - name: age 
          type: int
          cardinality: scalar
          required: true

"""

schema_duplicated_column = f"""

uri_constructor: 'tests.federation.schema_simple.FederatedUriTest'

types:


classes:

    - uri_prefix: person
      can_be_root: true 
      columns:
        - name: age 
          type: int
          cardinality: scalar
          required: true

        - name: age 
          type: real
          cardinality: scalar
          required: true

"""

schema_simple_yaml = f"""

uri_constructor: 'tests.federation.schema_simple.FederatedUriTest'

types:

    enums:
      
      fruits:
        - apple 
        - banana 
        - orange 


classes:
    - uri_prefix: '{TYPE_T1}'
      can_be_root: true 
      columns:
        - name: 'key_int'
          type: 'int'
          cardinality: 'scalar'
          required: true
        - name: int_none
          type: int
          cardinality: scalar
          required: false
        - name: 'key_str'
          type: 'str'
          cardinality: 'scalar'
          required: false
        - name: int_def
          type: int
          cardinality: scalar
          required: false
          default: 101
        - name: key1
          type: str
          cardinality: scalar
          required: false
        - name: uses
          type: local_uri
          cardinality: scalar
          required: false

    - uri_prefix: '{TYPE_T2}'
      can_be_root: false
      columns: []


    - uri_prefix: conflict_c
      can_be_root: true
      columns:
        - name: name
          type: str
          cardinality: scalar
          required: false
          default: "no name"

        - name: balance
          type: int
          cardinality: scalar
          required: false
          default: 0


    - uri_prefix: t_json
      can_be_root: false
      columns:
        - name: ob_json
          type: json
          cardinality: scalar
          required: true

    - uri_prefix: p_enum
      can_be_root: true
      columns:
        - name: name
          type: str
          cardinality: scalar
          required: true

        - name: preferred_fruit
          type: enum
          sub_type: fruits
          cardinality: scalar
          required: true

        - name: second_preferred_fruit
          type: enum
          sub_type: fruits
          cardinality: scalar
          required: false
          default: banana


    - uri_prefix: t_uri_set
      can_be_root: true
      columns:
        - name: members
          type: local_uri 
          cardinality: set
          required: true
          minimum_cardinality: 1


    - uri_prefix: t_member
      can_be_root: false
      columns:
        - name: name 
          type: str
          cardinality: scalar
          required: true


    - uri_prefix: al_uri
      can_be_root: true
      columns:
        - name: trust_lines
          type: uri
          cardinality: set
          required: false


    - uri_prefix: test_no_uri
      can_be_root: true 
      columns:
        - name: need_uri 
          type: uri
          cardinality: scalar
          required: true
    

    - uri_prefix: test_no_ref
      can_be_root: false
      columns:
        - name: need_uri 
          type: uri
          cardinality: scalar
          required: true


    - uri_prefix: tline
      can_be_root: false
      columns:
        - name: equity
          type: real
          cardinality: scalar
          required: false
          default: 10.0


    - uri_prefix: al
      can_be_root: true
      columns:
        - name: equity
          type: real
          cardinality: scalar
          required: true

        - name: family
          type: local_uri 
          cardinality: scalar
          required: true

"""


FIRST_HOST = "www.example.com"
OTHERHOST = "www.faraway.org"
LOCALHOST = 'localhost'
LOCALHOST1 = "::1"


