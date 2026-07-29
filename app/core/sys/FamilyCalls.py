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
from app.core.algo.utils import federated_transaction
from app.logging import gCon
from app.sdc.Dependencies import Dependencies

class FamilyCalls:

    @staticmethod
    @active_login
    async def _sys_call_invite(kernel, session, pars):
        invite_code = pars['invite_code']
        user_handle = pars['user_handle']
        social_gw = kernel.get_dep(Dependencies.SOCIAL_GATEWAY)
        user_dto = await social_gw.discover_user(user_handle)
        gCon.log(f"I will invite actor {user_dto.act.preferred_username}")
        social = kernel.get_dep(Dependencies.SOCIAL)
        social_api = kernel.get_dep(Dependencies.SOCIAL_API)
        social_user = social_api.get_social_user()
        this_host = kernel.conf().get_host()
        social_handle = f"@{social_user}@{this_host}"
        
        await social.out_msg_listener_to_actor(user_dto,
f"""You have been invited to join adelphos by @{session.alias_family}@{this_host}
 to accept it do a private mention 
 {social_handle} family.join alias $alias_chosen invite_code {invite_code}""")



    @staticmethod
    @active_login
    async def _sys_call_increase_equity(kernel, session, pars):
        pass
 

    @federated_transaction
    async def family_invite():
        pass
