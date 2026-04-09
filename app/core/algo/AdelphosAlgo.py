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

# the objects do NOT cross the boundary of the model,
# at the external we only see IDs or objects created from the basic objects.

# all models are federated! The difference is not in the model, but in the DB!
class AdelphosAlgo:


    # I have an instance id, an integer, this is then used to store the data in the same
    # db without clashes.
    def __init__(self, instance_id, db):
        self.db = db 
        self.instance_id = instance_id
        self.family_model  = FamilyModel(self.db)
        self.alias_model   = AliasModel(self.db)
        self.alias_algo    = AliasAlgo(self)
        #self.errno = 0



