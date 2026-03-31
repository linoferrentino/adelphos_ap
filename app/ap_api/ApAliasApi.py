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
# this is the ActivityPub alias API.
# In Activity Pub realm we only create an alias. 

from app.api.BaseApi import BaseApi
from app.dao.AdelphosUri import uriparse_type, EAdelphosType
from app.api.AdelphosException import AdelphosException
from app.logging import gCon
#from app.dao.FamilyDto import family_dto_create_local
from argon2 import PasswordHasher

class ApAliasApi(BaseApi):


    def __init__(self, gateway):
        super().__init__(gateway, HANDLERS)


    # here we define the handlers.
    async def _hndl_ap_alias_create(self):

        alias = self.gateway.get_param_safe('alias')
        password = self.gateway.get_param_safe('password')
        self.create_alias_pass(self.gateway.actor_dto.actor_id, alias, password)
        return f"Created alias {alias} successfully. You can login, now."


    def create_alias_pass(self, actor_id, alias, password):

        alias_uri = uriparse_type(alias, EAdelphosType.ALIAS_TYPE)

        if (alias_uri.is_numeric == True):
            raise AdelphosException("Cannot create a numeric alias")

        #gCon.log(f"alias uri created {alias_uri}")

        family_dto = self.gateway.app.dao.family_dao.get_from_local_name(
                alias_uri.family)

        if (family_dto is not None):
            raise AdelphosException(
f"family {alias_uri.family} is already existing in this instance")

        ph = PasswordHasher()
        pass_hashed = ph.hash(password)

        # we are creating here an alias in instance zero.
        self.gateway.app.dao.alias_dao.create_alias_impl(
            actor_id, alias_uri.family, 0, alias_uri.name, pass_hashed)


# this table is valid for all the objects
HANDLERS = {
     'alias_create' : ApAliasApi._hndl_ap_alias_create
}

