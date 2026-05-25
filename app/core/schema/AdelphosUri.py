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


from enum import StrEnum
from app.federation.FederatedUri import FederatedUri


class EAdelphosType(StrEnum):
    ALIAS_TYPE = 'al'


class AdelphosUri(FederatedUri):

    def unparse(self):
        base_name = "#" + self.ob_type + "#" + self.name

        if self.family is not None:
            base_name += f".{self.family}"
        if self.fragment is not None:
            base_name += f"#f{self.fragment}"
        if self.host is not None:
            base_name += f"@f{self.host}"

        return base_name




