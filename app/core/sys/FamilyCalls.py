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
import app.core.sys.family_utils as fu
import app.core.sys.task_utils as tku


class FamilyCalls:

    @staticmethod
    @active_login
    async def _sys_call_associate(kernel, session, pars):
        pars['_session'] = session
        await FamilyCalls._family_associate_safe(kernel, pars)
 

    @staticmethod
    @federated_transaction(raise_if_fail = True)
    async def _family_associate_safe(kernel, pars ,t_id):
        await FamilyCalls._family_associate_impl(kernel, pars, t_id)


    @staticmethod
    @active_login
    async def _sys_call_join(kernel, session, pars):
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
    async def _family_associate_impl(kernel, pars, t_id):
        family_src_ob = await scu.get_family_source(kernel, pars, t_id)
        scu.ensure_logged_alias_is_boss(family_src_ob, pars)

        family_session_str = await scu.get_family_str_in_session(kernel,
                                pars, t_id)
        gCon.log(f"The family session str {family_session_str}")

        family_dst_ob = await scu.get_family_dest(kernel, pars, t_id)

        level_src = family_src_ob().get_scalar('level')
        level_dst = family_dst_ob().get_scalar('level')

        if level_src != level_dst:
            raise AdelphosCoreException(ECoreErrno.EDIFFERENT_LEVELS,
              f"Family src level {level_src} family_dst level {level_dst}")

        family_src_chain = await scu.get_family_chain_up_from_to_str(kernel,
                family_session_str, family_src_ob, t_id)

        gCon.log(f"The family src chain is {family_src_chain}")

        scu.ensure_family_not_associated(family_src_ob)
        scu.ensure_family_not_associated(family_dst_ob)

        boss_ob = await fu.family_get_your_boss(kernel, family_dst_ob, t_id)

        family_boss_uri = AdelphosUri(EAdelphosType.FAMILY_TYPE,
              boss_ob().uri.family, host = boss_ob().uri.host)

        family_dst_chain = await scu.get_family_chain_up_from_to_str(kernel,
                family_boss_uri.unparse(), family_dst_ob, t_id)
        gCon.log(f"The family_dst_chain is {family_dst_chain}")

        pars['family_src_chain'] = family_src_chain
        pars['family_dst_chain'] = family_dst_chain

        await tku.add_task_to_alias(kernel, boss_ob, 'associate_family',
                                  pars, t_id)


    @staticmethod
    async def _family_add_invite_impl(kernel, pars, t_id):
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


