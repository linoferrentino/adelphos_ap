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

types:

    enums:
      currency:
        - APH
        - EUR
        - USD
        - GBP
        - CHF
        - JPY

classes:

    - uri_prefix: {EAdelphosType.ALIAS_TYPE}
      can_be_root: false 

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

        - name: inbox
          type: json
          cardinality: array
          required: false


    - uri_prefix: {EAdelphosType.FAMILY_TYPE}
      can_be_root: true

      columns:

        - name: equity
          type: real
          cardinality: scalar
          required: false
          default: 0.0

        - name: trust
          type: real
          cardinality: scalar
          required: false
          default: 0.0

        - name: currency
          type: enum
          sub_type: currency
          cardinality: scalar
          required: false
          default: EUR

        - name: invite
          type: json 
          cardinality: scalar
          required: false

        - name: boss
          type: local_uri 
          cardinality: scalar
          required: true

        - name: members
          type: local_uri 
          cardinality: set
          required: true

        - name: board_ask
          type: uri
          cardinality: array
          required: false

        - name: board_bid
          type: uri
          cardinality: array
          required: false



    - uri_prefix: {EAdelphosType.GROUP_TYPE}
      can_be_root: false

      columns:

        - name: multiplier
          type: real
          cardinality: scalar
          required: false
          default: 0.20

        - name: level
          type: int
          cardinality: scalar
          required: true

        - name: members
          type: uri 
          cardinality: set
          required: true

        - name: boss
          type: uri 
          cardinality: scalar
          required: true

        - name: judge
          type: uri 
          cardinality: scalar
          required: true

        - name: vice
          type: uri 
          cardinality: scalar
          required: true

        - name: equity
          type: real
          cardinality: scalar
          required: false
          default: 0.0


"""


