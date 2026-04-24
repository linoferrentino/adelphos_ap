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

# the federated object alias

from app.federation.FederatedObject import FederatedObject
from app.federation.FederatedObject import FObColumnDefinition, FObColType, \
        FObCardType, FObReqType

from app.core.model.AdelphosUri import AdelphosUri
from app.core.model.AdelphosUri import EAdelphosType

from app.federation.FederatedFactory import FederatedFactory
from app.federation.FederatedFactory import FederatedFactoryRegistrar

class AliasFob(FederatedObject):

    @classmethod
    def register_class(cls):
        reg = FederatedFactoryRegistrar(cls, True, True)
        FederatedFactory._register_ob_type(cls._type, reg)
 

    _type = EAdelphosType.ALIAS_TYPE

    _schema = {

            'actor_id' : FObColumnDefinition(
                FObColType.INTEGER,
                FObCardType.SCALAR,
                FObReqType.REQUIRED
                ),

            #'name' : FObColumnDefinition(
            #    FObColType.STRING,
            #    FObCardType.SCALAR,
            #    FObReqType.REQUIRED
            #    ),

            'password' : FObColumnDefinition(
                FObColType.STRING,
                FObCardType.SCALAR,
                FObReqType.REQUIRED
                ),

            #'family' : FObColumnDefinition(
            #    FObColType.URI,
            #    FObCardType.SCALAR,
            #    FObReqType.REQUIRED
            #    )

    }

    @classmethod
    def get_schema(cls):
        return cls._schema


