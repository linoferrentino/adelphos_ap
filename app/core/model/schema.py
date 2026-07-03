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
from app.core.model.AdelphosUri import AdelphosUri
from app.core.model.AdelphosUri import EAdelphosType

#from app.core.model.AliasFob import AliasFob
#from app.core.model.FamilyFob import FamilyFob

#def adelphos_schema_fn():
#
#    FederatedFactory.set_uri_constructor(AdelphosUri)
#    
#    AliasFob.register_class()
#    FamilyFob.register_class()


adelphos_schema_yaml = f"""

uri_constructor: app.core.model.AdelphosUri.AdelphosUri

classes:
    - uri_prefix: {EAdelphosType.ALIAS_TYPE}
      first_class: true
      needs_family: true
      columns:
        - name: actor_id
          type: int
          cardinality: scalar
          required: true

        - name: key_str
          type: str
          cardinality: scalar
          required: false
"""


