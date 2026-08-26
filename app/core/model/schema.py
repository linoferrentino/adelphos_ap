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
        - APC
        - AUD
        - CAD
        - CHF
        - CNY
        - EUR
        - GBP
        - JPY
        - NZD
        - USD

classes:

    - uri_prefix: {EAdelphosType.ALIAS_TYPE}
      can_be_root: false 

      columns:

        - name: actor_handle
          type: str
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

        - name: level
          type: int
          cardinality: scalar
          required: true

        - name: shared_ratio 
          type: real
          cardinality: scalar
          required: false
          default: 0.15

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
          type: uri 
          cardinality: scalar
          required: true

        - name: members
          type: uri 
          cardinality: set
          required: true
          minimum_cardinality: 1

        - name: agora
          type: uri
          cardinality: scalar
          required: true
        
        - name: upper_family
          type: uri
          cardinality: scalar
          required: false

        - name: balance
          type: real
          cardinality: scalar
          required: false
          default: 0.0

        - name: inbox
          type: uri
          cardinality: set
          required: false


    - uri_prefix: {EAdelphosType.AGORA_TYPE}
      can_be_root: false

      columns:

        - name: location
          type: str
          cardinality: scalar
          required: false
          default: not set

        - name: family
          type: uri
          cardinality: scalar
          required: true

        - name: offers
          type: uri
          cardinality: set
          required: false

        - name: watcher
          type: uri
          cardinality: scalar
          required: true

        - name: export_box
          type: uri
          cardinality: set
          required: false

        - name: import_box 
          type: uri
          cardinality: set
          required: false


    - uri_prefix: {EAdelphosType.OBJECT_TYPE}
      can_be_root: false

      columns:

        - name: sender 
          type: uri
          cardinality: scalar
          required: true

        - name: recipient
          type: uri
          cardinality: scalar
          required: false

        - name: description
          type: str
          cardinality: scalar
          required: true

        - name: price
          type: real
          cardinality: scalar
          required: true



"""


