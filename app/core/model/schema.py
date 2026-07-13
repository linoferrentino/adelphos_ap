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


from app.federation.FederatedFactory import FederatedFactory
from app.core.model.AdelphosUri import AdelphosUri
from app.core.model.AdelphosUri import EAdelphosType


adelphos_schema_yaml = f"""

uri_constructor: app.core.model.AdelphosUri.AdelphosUri

classes:

    - uri_prefix: {EAdelphosType.ALIAS_TYPE}
      can_be_root: true

      columns:

        - name: actor_id
          type: int
          cardinality: scalar
          required: true

        - name: password
          type: str
          cardinality: scalar
          required: true

        - name: tasks
          type: json 
          cardinality: array
          required: false

    - uri_prefix: {EAdelphosType.FAMILY_TYPE}
      can_be_root: false

      columns:

        - name: equity
          type: real
          cardinality: scalar
          required: false

        - name: invites
          type: json 
          cardinality: array
          required: false

        - name: boss
          type: local_uri 
          cardinality: scalar
          required: true

        - name: members
          type: local_uri 
          cardinality: set
          required: true

"""


