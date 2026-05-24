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
from app.federation.FederatedObject import FederatedObject
from app.federation.FederatedObject import FObColumnDefinition, FObColType, \
        FObCardType, FObReqType


class AliasClass(FederatedObject):

    _schema = {
            'reputation' : FObColumnDefinition(
                FObColType.REAL,
                FObCardType.SCALAR,
                FObReqType.NO_REQUIRED_DEFAULT_VALUE,
                0
                ),
            }

    def __init__(self, uri, ref_count, **kwargs):
        super().__init__(uri, ref_count, **kwargs)


    @classmethod
    def get_schema(cls):
        return cls._schema

    
    @classmethod
    def register_class(cls):
        reg = FederatedFactoryRegistrar(AliasClass, True, True)
        FederatedFactory._register_ob_type(AdelphosType.ALIAS_TYPE, reg)



