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


import json
from app.api.UserSession import active_login
from app.core.algo.utils import federated_transaction
from app.sdc.Dependencies import Dependencies
from app.core.model.AdelphosUri import EAdelphosType
from app.core.model.AdelphosUri import AdelphosUri
from app.core.AdelphosCoreException import AdelphosCoreException
from app.core.ECoreErrno import ECoreErrno

from app.logging import gCon

import app.core.sys.sys_calls_utils as scu


class FamilyCalls:

    @staticmethod
    @active_login
    async def _sys_call_invite_family(kernel, session, pars):
        pass
 

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

        pars['_session'] = session
        await FamilyCalls._family_add_invite_safe(kernel, pars)
        
        await social.out_msg_listener_to_actor(user_dto,
f"""You have been invited to join adelphos by @{session.alias_family}@{this_host}
 to accept it do a private mention 
 {social_handle} family.join alias $alias_chosen invite_code {invite_code}""")


    @staticmethod
    @federated_transaction(raise_if_fail = True)
    async def _family_add_invite_safe(kernel, pars ,t_id):
        await FamilyCalls._family_add_invite_impl(kernel, pars, t_id)


    @staticmethod
    async def _family_add_invite_impl(kernel, pars, t_id):

        #family = pars['_session'].family
        user_handle = pars['user_handle']
        invite_code = pars['invite_code']

        family_ob = await scu.get_family_in_session(kernel, pars, t_id)

        scu.ensure_logged_alias_is_boss(family_ob, pars)

        invite_ob = family_ob().get_scalar('invite')
        if invite_ob is not None:
            raise AdelphosCoreException(ECoreErrno.EINVITE_ALREADY_PRESENT,
                                        json.dumps(invite_ob))
        invite_ob = {
                'user_handle' : user_handle,
                'invite_code' : invite_code,
        }

        family_ob().set_scalar('invite', invite_ob)


