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

# the model part for the family

from app.federation.FederatedObject import FederatedObject
from app.federation.FederatedObject import FObColumnDefinition, FObColType, \
        FObCardType, FObReqType

from app.core.model.AdelphosUri import AdelphosUri
from app.core.model.AdelphosUri import EAdelphosType

from app.federation.FederatedFactory import FederatedFactory
from app.federation.FederatedFactory import FederatedFactoryRegistrar


class FamilyFob(FederatedObject):

    @classmethod
    def register_class(cls):
        reg = FederatedFactoryRegistrar(cls, False, False)
        FederatedFactory._register_ob_type(cls._type, reg)
 

    _type = EAdelphosType.FAMILY_TYPE

    _schema = {

    }

    @classmethod
    def get_schema(cls):
        return cls._schema


