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
from app.dao.AdelphosUri import uriparse
from app.api.AdelphosException import AdelphosException
from app.logging import gCon
from app.dao.FamilyDto import family_dto_create_local
from argon2 import PasswordHasher
from app.dao.AliasDto import alias_dto_create_local

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

        alias_uri = uriparse(alias)

        if (alias_uri.is_numeric == True):
            raise AdelphosException("Cannot create a numeric alias")

        gCon.log(f"alias uri created {alias_uri}")

        family_dto = self.gateway.app.dao.family_dao.get_from_local_name(
                alias_uri.family)

        if (family_dto is not None):
            raise AdelphosException(
f"family {alias_uri.family} is already existing in this instance")

        ph = PasswordHasher()
        pass_hashed = ph.hash(password)

        self.create_alias_impl(actor_id, alias_uri.family, alias_uri.name,
                    pass_hashed)

    
    # this function will simply use the fields and store the rows in db.
    # this function bypasses all checks! Call it only after validating user input
    def create_alias_impl(self, actor_id, family, name, password_hashed):

         # let's create the family, for now it will have only a name, not a currency
        family_dto = family_dto_create_local(family)

        family_id = self.gateway.app.dao.family_dao.store(family_dto)

        # I use the activity pub actor object to link to the alias
        alias_dto = alias_dto_create_local(name,
                   actor_id, family_id, password_hashed)

        # OK, let't try to add it to the database
        new_id = self.gateway.app.dao.alias_dao.store(alias_dto)

        return new_id


# this table is valid for all the objects
HANDLERS = {
     'alias_create' : ApAliasApi._hndl_ap_alias_create
}

