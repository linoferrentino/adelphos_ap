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

# the family model of adelphos


from app.core.BaseModel import BaseModel
from app.dao.AdelphosUri import AdelphosUri
from app.dao.AdelphosUri import EAdelphosType


FM_BOSS_KEY = 'fm_boss_key'


# in the db we put the objects with their URIs, the numerical URI and
# the human uri.


class FamilyModel(BaseModel):


    def __init__(self, db):
        super().__init__(db, EAdelphosType.FAMILY_TYPE)


    def create(self, name):
        return super().create_base(name)


    def set_boss(self, fam_ob, alias_ob):
        fam_ob[FM_BOSS_KEY] = alias_ob

        




