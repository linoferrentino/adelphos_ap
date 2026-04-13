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

# the local model is the class that has the logic to
# handle the core of adelphos
# the fractal trust network, the exchange of credits

# it has not a concept of a social network, this
# is on another layer on top of it.

from app.dao.FamilyDao import FamilyDao
from app.dao.AliasDao import AliasDao
from app.core.EAdErrno import EAdErrno
from app.core.FamilyModel import FamilyModel
from app.core.AliasModel import AliasModel
from app.core.BaseIdModel import AD_INVALID_ID
from app.core.BaseModel import BaseModel
from app.core.algo.AliasAlgo import AliasAlgo
from app.logging import gCon
from argon2 import PasswordHasher


# the local model is always consistent. Every method called
# is part of a transaction.
# the local mode uses the URI as the identifier.
# all models are federated! The difference is not in the model, but in the DB!
class AdelphosAlgo:


    def __init__(self, instance_id, db):
        self.db = db 
        self.instance_id = instance_id
        self.family_model  = FamilyModel(self.db)
        self.alias_model   = AliasModel(self.db)
        self.alias_algo    = AliasAlgo(self)


