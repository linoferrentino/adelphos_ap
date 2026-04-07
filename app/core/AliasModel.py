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

# the Alias Model used to store and retrieve Alias objects

from app.dao.AdelphosUri import EAdelphosType
from app.core.BaseModel import BaseModel
from app.core.BaseModel import AD_NAME_KEY
#from app.core.BaseModel import AD_ID_KEY
from app.core.BaseModel import AD_ACTOR_ID_KEY
from app.core.BaseIdModel import BaseIdModel

AD_ALIAS_FAM_ID = 'ad_family_id'
AD_ALIAS_PASSWORD = 'ad_password'


class AliasModel(BaseModel):


    def __init__(self, db):
        super().__init__(db, EAdelphosType.ALIAS_TYPE)


    def create(self, actor_id, alias_name, fam_dto, pass_hashed):

        new_alias = self.create_base(alias_name, fam_dto[AD_NAME_KEY])

        new_alias[AD_ACTOR_ID_KEY] = actor_id
        new_alias[AD_ALIAS_FAM_ID] = BaseIdModel.get_id(fam_dto)
        new_alias[AD_ALIAS_PASSWORD] = pass_hashed

        self.db.update(new_alias)

        return new_alias

