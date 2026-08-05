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



# Every object in adelphos is identified by this URI

from enum import StrEnum
from app.federation.FederatedUri import FederatedUri
from dataclasses import dataclass
from app.exc.AdelphosException import AdelphosException
from app.exc.AdelphosException import AdErrno
from app.logging import gCon
import app.misc.alias_utils as au


class EAdelphosType(StrEnum):
    ALIAS_TYPE = 'al'
    FAMILY_TYPE = 'fa'
    GROUP_TYPE = 'gr'
    TRUST_LINE_TYPE = 'tr'


@dataclass
class AdelphosUri(FederatedUri):

    family: str = None

    def unparse(self, force_local = False):

        if self.ob_type == EAdelphosType.ALIAS_TYPE:
            uri_local = f"#{self.ob_type}#{self.name}.{self.family}"
        else:
            uri_local = f"#{self.ob_type}#{self.name}"

        if self.fragment is not None:
            uri_local += f"#{self.fragment}"

        if force_local == False:
            uri_local += self._base_get_host_part()

        return uri_local
     

    def create_uri(uri_type, name_part, *, host_part = None, fragment = None):
        (alias, family) = au.split_alias(name_part, True)
        uri = AdelphosUri(uri_type, alias, family = family,
                          host = host_part, fragment = fragment)
        return uri
     
