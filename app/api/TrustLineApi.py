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

class TrustLineApi:

    def __init__(self, ctx):
        self.ctx = ctx


    # this function might download information from other adelphos instances
    # so it is async.
    async def create(self):
        alias_to = self.ctx.get_param_safe('alias_to')
        alias_uri = uriparse_type(alias, EAdelphosType.ALIAS_TYPE)

        # Now I have to get this object, it does not matter where it is,
        # so I await for it.
        alias_to_ob = await self.ctx.app.dao.alias_dao.get_from_uri(alias_uri)

        # If I am here the alias is existing, I have to know if the trust line
        # is existing and create it. To do.

        return f"Creating a trust line to {alias_uri} which is {alias_to_ob}"

