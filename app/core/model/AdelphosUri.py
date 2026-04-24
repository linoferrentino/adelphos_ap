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


# Every object in adelphos is identified by this URI

from enum import StrEnum
from app.federation.FederatedUri import FederatedUri


class EAdelphosType(StrEnum):
    ALIAS_TYPE = 'al'
    FAMILY_TYPE = 'fa'
    GROUP_TYPE = 'gr'
    TRUST_LINE_TYPE = 'tr'


class AdelphosUri(FederatedUri):


    def unparse(self):

        if self.ob_type == EAdelphosType.ALIAS_TYPE:
            uri_local = f"#{self.ob_type}#{self.name}.{self.family}"
        else:
            uri_local = f"#{self.ob_type}#{self.name}"

        if self.fragment is not None:
            uri_local += f"#{self.fragment}"

        if self.host is None:
            return uri_local

        uri_local += f"@{self.host}"
        return uri_local

     
