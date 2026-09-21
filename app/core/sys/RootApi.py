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

import re
import json
import traceback
from app.logging import gCon

from app.core.model.AdelphosUri import EAdelphosType
from app.core.model.AdelphosUri import AdelphosUri
from app.core.algo.utils import federated_transaction
from app.core.AdelphosCoreException import AdelphosBaseException
from app.exc.AdelphosException import AdelphosException
from app.exc.AdelphosException import AdErrno
from app.sdc.Dependencies import Dependencies
from app.core.algo.AliasAlgo import AliasAlgo
from app.core.sys.AliasCalls import AliasCalls

import app.core.sys.FamilyCalls as fcalls
import app.core.sys.family_utils as fu
import app.misc.alias_utils as au
import app.core.sys.alias_utils as autils
import app.core.sys.offer_utils as ofutils
import app.core.sys.agora_utils as agu
import app.core.sys.ecommerce_utils as ecut
import app.core.sys.AgoraCalls as ac


def sudo_cmd(func):

    async def check_root(kernel, session, pars):
        if (session.is_logged_root() == False):
            raise AdelphosException(AdErrno.EPERM, "You need to be root.")
        if (pars.get('force') == True):
            pars['_unsafe'] = True

        return await func(kernel, session, pars)
    
    return check_root



class RootApi:

    @sudo_cmd
    @staticmethod
    async def _sys_call_play_script(kernel, session, pars):
        await _root_play_script(kernel, session, pars)


    @sudo_cmd
    @staticmethod
    async def _sys_call_clear_cache(kernel, session, pars):
        fdb = kernel.get_dep(Dependencies.FEDERATED_DB)
        fdb.empty_cache()


    @sudo_cmd
    @staticmethod
    async def _sys_call_buy_object_title(kernel, session, pars):
        await _root_buy_object_title_safe(kernel, pars)


    @sudo_cmd
    @staticmethod
    async def _sys_call_put_object(kernel, session, pars):
        await _root_put_object_safe(kernel, pars)


    @sudo_cmd
    @staticmethod
    async def _sys_call_allow_remote(kernel, session, pars):
        host = pars['host']
        social_api = kernel.get_dep(Dependencies.SOCIAL_API)
        user_tag = social_api.remote_host_allow(host)


    @sudo_cmd
    @staticmethod
    async def _sys_call_deny_remote(kernel, session, pars):
        host = pars['host']
        social_api = kernel.get_dep(Dependencies.SOCIAL_API)
        user_tag = social_api.remote_host_deny(host)


    @staticmethod
    async def _sys_call_pop_alias(kernel, session, pars):
        popped_session = session.client.pop_session()
        return popped_session.get_alias_ob().ob.fields


    @sudo_cmd
    @staticmethod
    async def _sys_call_push_alias(kernel, session, pars):
        return await _push_alias_safe(kernel, pars)



    @sudo_cmd
    @staticmethod
    async def _sys_call_add_user(kernel, session, pars):
        await _get_user_impl(kernel, session, pars, create = True)


    @sudo_cmd
    @staticmethod
    async def _sys_call_add_user_alias(kernel, session, pars):
        return await _sys_call_add_user_alias_impl(kernel, session, pars,
                                create = True)


    @sudo_cmd
    @staticmethod
    async def _sys_call_add_alias(kernel, session, pars):
        return await _sys_call_add_user_alias_impl(kernel, session, pars,
                                create = False)


    @sudo_cmd
    @staticmethod
    async def _sys_call_alias_join_family(kernel, session, pars):
        pars['_session'] = session
        return await _alias_join_family_safe(kernel, pars)


    @sudo_cmd
    @staticmethod
    async def _sys_call_do_association(kernel, session, pars):
        pars['_session'] = session
        await _do_association_safe(kernel, pars)


@federated_transaction(raise_if_fail = True)
async def _push_alias_safe(kernel, pars, t_id):
    alias = pars['alias']
    session = pars['_param']
    alias_session = await _push_alias_impl(kernel, session, alias, t_id)
    return alias_session.get_alias_ob().ob.fields


async def _push_alias_impl(kernel, session, alias, t_id):
    gCon.log(f"pushing alias {alias}")
    alias_session = session.client.push_session(alias)
    await AliasCalls._session_login(kernel, alias_session,
                                    alias, None, t_id, True)
    return alias_session


@federated_transaction(raise_if_fail = True)
async def _root_buy_object_title_safe(kernel, pars, t_id):
    as_adelphos_uri_str = pars['as_adelphos']
    object_title = pars['ad_title']
    session = pars['_param']

    alias_session = await _push_alias_impl(kernel, session,
                            as_adelphos_uri_str, t_id)
    pars['_param'] = alias_session
    gCon.log(f"after push session is {alias_session} with family {alias_session.family}") 

    session = pars['_param']
    hearts_given = pars['hearts_given']
    pars['_x_skip_task'] = True

    try:
        (exp_chain, imp_chain) = await agu._agora_buy_object_impl(
                kernel, pars, t_id)
        await ecut.complete_buy_task(kernel, hearts_given,
                        exp_chain, imp_chain, t_id)
    finally:
        session.client.pop_session()
 
   
@federated_transaction(raise_if_fail = True)
async def _root_put_object_safe(kernel, pars, t_id):
    gCon.log(f"Add object with pars {pars}")
    fdb = kernel.get_dep(Dependencies.FEDERATED_DB)
    as_adelphos_uri_str = pars['as_adelphos']
    alias_ob = await fdb.uri_read_str(t_id, as_adelphos_uri_str,
                                      must_lock = True)
    family_ob = await autils.alias_get_your_family(kernel,
            as_adelphos_uri_str, t_id)
    gCon.log(f"aliasob {alias_ob} family {family_ob}")
    await ofutils.object_put_ad_in_agora_impl(kernel, family_ob,
            alias_ob, pars, t_id)
    

@federated_transaction(raise_if_fail = True)
async def _do_association_safe(kernel, pars, t_id):
    await fcalls._family_associate_first_half(kernel, pars, t_id)
    await fu.family_associate_2nd_half(kernel, pars, t_id)


@federated_transaction(raise_if_fail = True)
async def _alias_join_family_safe(kernel, pars, t_id):

    family = pars['family']
    user = pars['user']
    alias = pars['alias']
    password = pars['password']

    fdb = kernel.get_dep(Dependencies.FEDERATED_DB)

    host = kernel.conf().get_host()

    user_handle = f"@{user}@{host}"

    family_uri = AdelphosUri(EAdelphosType.FAMILY_TYPE, family)
    family_ob = await fdb.uri_read_ob(t_id, family_uri, must_lock = True)

    alias_ob = await AliasAlgo._alias_add_in_family(fdb, family_ob, 
        user_handle, alias, family, password, t_id)
    return f"Created alias {alias_ob().uri.unparse()}"


 
async def _sys_call_add_user_alias_impl(kernel, session, pars,
                                        *, create = True):
    local_user = await _get_user_impl(kernel, session, pars, create = create)

    alias = pars['alias']

    (alias_name, family) = au.split_alias(alias, True)

    pars['actor_id'] = local_user.actor_dto.act.actor_id
    pars['alias_name'] = alias_name
    pars['family']  = family
    pars['user_handle'] = local_user.actor_dto.get_social_handle()

    return await AliasAlgo.alias_create_safe(kernel, pars) 


async def _get_user_impl(kernel, session, pars, *, create = False):
    social = kernel.get_dep(Dependencies.SOCIAL)
    user = pars['user']
    local_user = social.local_user_get(user, create_if_not_exists = False)
    if create == False and local_user is None:
        raise AdelphosException(AdErrno.USER_DOES_NOT_EXIST, user)
    elif create == False:
        return local_user
    if local_user is not None:
        raise AdelphosException(AdErrno.USER_ALREADY_EXISTING, user)
    local_user = social.local_user_get(user, create_if_not_exists = True)
    return local_user


async def _process_meta_line(kernel, session, pars, data):
    gCon.log(f"Process meta line {data} last res {pars['$?']}")
    (meta_cmd, meta_args) = data.split("|")
    meta_cmd = meta_cmd.strip()
    meta_args = meta_args.strip()
    gCon.log(f"meta_cmd {meta_cmd} args {meta_args}")
    match meta_cmd:
        case 'pop_msg':
            user = session.social_user
            gCon.log(f"I will store the last message of user {user}")
            user_inbox = kernel.get_dep(Dependencies.SOCIAL).local_user_get(user)
            msg = user_inbox.pop_lst_msg()
            gCon.log(f"Last message is {msg}")
            pars['$msg'] = msg

        case 'set_data':
            gCon.log(f"evaluate {meta_args} pars {pars['$?']} type {type(pars['$?'])}")
            exec(meta_args)
        case _:
            raise AdelphosException(AdErrno.ESCRIPT_ERROR,
                    f"Unrecognized meta command {meta_cmd}")


async def _root_play_line(kernel, session, pars, line):
    gCon.rule(f"processing ->{line[:50]}<-")

    if "==>" in line:
        (data, exps) = line.split("==>")
        exp = json.loads(exps)
    else:
        data = line
        exp = {
                'errno' : 0
        }

    data = data.format(**pars)

    gCon.log(f"Play line |{data}| with exp |{exp}|")

    if re.match(r"\$ ", data) is not None:
        data = re.sub(r"\$ ", "", data)
        await _process_meta_line(kernel, session, pars, data)
        return

    try:
        res_ob = await session.client.direct_gateway_call(data, dict_output = True)
        gCon.log(f"result {res_ob} type {type(res_ob)}")
        #res_ob = json.loads(res_str)
    except AdelphosBaseException as ex:
        gCon.log(f"Got Adelphos exception {ex}")
        traceback.print_exc()
        res_ob = {
           'errno' : ex.errno,
           'res' : ex.out_str
        }
    except Exception as ex:
        gCon.log(f"Got generic exception {ex}")
        traceback.print_exc()
        res_ob = {
           'errno' : AdErrno.ESYS,
           'res' : str(ex),
        }
    pars['$?'] = res_ob
    if (res_ob['errno'] != exp['errno']):
        raise AdelphosException(AdErrno.ESCRIPT_ERROR, res_str)
    eval_exp = exp.get('eval_exp')
    if eval_exp is not None:
        gCon.log(f"evaluating {eval_exp}")
        eval_result = eval(eval_exp)
        if eval_result != True:
            raise AdelphosException(AdErrno.ESCRIPT_ERROR,
                    f"failing of {eval_exp}")
       
    exp_re = exp.get('res_re')
    if exp_re is None:
        return
    if re.search(exp_re, res_ob['res']) is None:
        raise AdelphosException(AdErrno.ESCRIPT_ERROR,
                    f"Not found {exp_re} in {res_ob['res']}")


async def _root_play_script(kernel, session, pars):
    gCon.log(f"Playing the script {pars['script_path']}")
    with open (f"tests/scripts/{pars['script_path']}.as") as script:
        multiline = False
        long_line = ""
        for line in script:
            line = line.strip()
            if len(line) == 0:
                continue
            if line[0] == '#':
                continue
            if line[-1] == "\\":
                multiline = True
                long_line += line[:-1]
                continue
            if multiline:
                long_line += line
            else:
                long_line = line
                
            await _root_play_line(kernel, session, pars, long_line)
            long_line = ""


