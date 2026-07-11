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


from app.api.UserSession import active_login


class FamilyCalls:

    @staticmethod
    @active_login
    async def _sys_call_invite(kernel, session, pars):
        pass
 
