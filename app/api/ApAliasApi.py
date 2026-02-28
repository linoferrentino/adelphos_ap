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

class ApAliasApi(BaseApi):


    def __init__(self, gateway):
        super().__init__(gateway, HANDLERS)


    # here we define the handlers.
    async def _hndl_ap_alias_create(self):
        return "It works! _hndl_create_ap_alias"


# this table is valid for all the objects
HANDLERS = {
     'alias_create' : ApAliasApi._hndl_ap_alias_create
}

