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


from app.core.algo.AliasAlgo import AliasAlgo
from app.core.algo.FamilyAlgo import FamilyAlgo

class AdelphosAlgo:


    def __init__(self, fdb):
        self.fdb = fdb 

        self.alias_algo    = AliasAlgo(self)
        self.family_algo   = FamilyAlgo(self)


