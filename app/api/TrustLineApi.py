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
# This class implements the trust line API, it creates and manages the
# trust lines between aliases in adelphos.

# This class does not do the routing which is handled by the router object

from app.dao.AdelphosUri import uriparse_type
from app.dao.AdelphosUri import EAdelphosType
from app.api.BaseApi import BaseApi

from app.dao.AdelphosUri import uriparse
from app.dao.AdelphosUri import EAdelphosType

class TrustLineApi(BaseApi):


    def __init__(self, gateway):
        super().__init__(gateway, HANDLERS)


    # this function might download information from other adelphos instances
    # so it is async.
    async def _hndl_tl_create(self):

        # to create a trust line I need at least another alias and a judge.
        # they might not be in the same instance.
        alias_to = self.gateway.get_param_safe("alias_to")
        alias_to_uri = uriparse_type(alias_to, EAdelphosType.ALIAS_TYPE)
        judge = self.gateway.get_param_safe("judge")
        judge_uri = uriparse_type(judge, EAdelphosType.ALIAS_TYPE)

        return f"Trust line created from {alias_to} to {judge}\n\
They will need to confirm it before it is operational."


    async def _hndl_tl_create__old(self):
        alias_to = self.ctx.get_param_safe('alias_to')
        alias_uri = uriparse_type(alias, EAdelphosType.ALIAS_TYPE)

        # Now I have to get this object, it does not matter where it is,
        # so I await for it.
        alias_to_ob = await self.ctx.app.dao.alias_dao.get_from_uri(alias_uri)

        # If I am here the alias is existing, I have to know if the trust line
        # is existing and create it. To do.

        return f"Creating a trust line to {alias_uri} which is {alias_to_ob}"


# here the handlers for this API
HANDLERS = {
     'trust_line_create' : TrustLineApi._hndl_tl_create,
}


