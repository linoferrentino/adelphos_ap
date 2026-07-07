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


from app.sdc.Dependency import Dependency
from app.core.algo.AliasAlgo import AliasAlgo
from app.core.algo.FamilyAlgo import FamilyAlgo


class AdelphosAlgo_deprecated(Dependency):

    def __init__(self, kernel):
        super().__init__(kernel)

        self.alias_algo    = AliasAlgo(self)
        self.family_algo   = FamilyAlgo(self)


