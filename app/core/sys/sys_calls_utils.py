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

from app.sdc.Dependencies import Dependencies
from app.core.model.AdelphosUri import EAdelphosType
from app.core.model.AdelphosUri import AdelphosUri

from app.core.ECoreErrno import ECoreErrno
from app.core.AdelphosCoreException import AdelphosCoreException
import app.core.sys.alias_utils as au

from app.logging import gCon


async def _is_alias_in_family_chain(kernel, alias_ob, family_str, t_id):
    fdb = kernel.get_dep(Dependencies.FEDERATED_DB)
    family_ob = await fdb.uri_read_str(t_id, family_str)
    lev_family = await family_ob().get_scalar('level', t_id)
    family0 = await au.alias_ob_get_your_family(kernel, alias_ob, t_id)
    chain_up = await get_family_chain_up_l(kernel, family0, lev_family, t_id)
    top_fam = chain_up[-1]
    if top_fam().uri.unparse() == family_ob().uri.unparse():
        return True
    return False


async def _ensure_alias_in_families(kernel, alias_ob, families, t_id):
    for family in families:
        gCon.log(f"_searching in family {family}")
        res = await _is_alias_in_family_chain(kernel, alias_ob, family, t_id)
        if res == True:
            return
    raise AdelphosCoreException(ECoreErrno.EEXTERNAL_ALIAS,
            f"alias {alias_ob().uri.unparse()} is external in family list")


async def get_family_str_in_session(kernel, pars, t_id):
    family_uri = pars['_param'].family_uri
    return family_uri.unparse()


async def get_family_in_session(kernel, pars, t_id):
    family = pars['_param'].family
    fdb = kernel.get_dep(Dependencies.FEDERATED_DB)
    family_uri = AdelphosUri(EAdelphosType.FAMILY_TYPE, family)
    family_ob = await fdb.uri_read_ob(t_id, family_uri, must_lock = True,
                                      only_local = True)
    return family_ob


async def get_family_source(kernel, pars, t_id):
    family_source = pars.get('family_source')
    if family_source is None:
        family_ob = await get_family_in_session(kernel, pars, t_id)
        pars['family_source'] = pars['_param'].family_uri.unparse()
        return family_ob
    fdb = kernel.get_dep(Dependencies.FEDERATED_DB)
    family_ob = await fdb.uri_read_str(t_id, family_source,
                must_lock = True)
    return family_ob


async def get_family_dest(kernel, pars, t_id):
    family_dest = pars.get('family_dest')
    fdb = kernel.get_dep(Dependencies.FEDERATED_DB)
    family_ob = await fdb.uri_read_str(t_id, family_dest,
                must_lock = True)
    return family_ob


async def get_family_chain_up(kernel, pars, t_id):
    family_ob = await get_family_in_session(kernel, pars, t_id)
    uplevel = pars['uplevel']
    return await get_family_chain_up_l(kernel, family_ob, uplevel, t_id)


async def get_family_chain_up_l(kernel, family_ob, uplevel, t_id):
    chain = list()
    fdb = kernel.get_dep(Dependencies.FEDERATED_DB)
    chain.append(family_ob)
    gCon.log(f"Starting chain up from {family_ob().uri.unparse()}")
    for lev in range(0, uplevel):
        family_uri = await family_ob().get_scalar('upper_family', t_id)
        if family_uri is None:
            raise AdelphosCoreException(ECoreErrno.EUPLEVEL_NOT_FOUND,
                                        f"lev {lev+1} not found")
        family_ob = await fdb.uri_read_str(t_id, family_uri, must_lock = True)
        chain.append(family_ob)
    return chain


async def get_family_chain_up_from_to_str(kernel,
                family_uri_src, family_to_ob, t_id):
    chain_obs = await get_family_chain_up_from_to(kernel,
                family_uri_src, family_to_ob, t_id)
    return transform_chain_ob_to_str(chain_obs)


def transform_chain_ob_to_str(chain_obs):
    chain_str = list()
    for chain_ob in chain_obs:
        chain_str.append(chain_ob().uri.unparse())
    return chain_str


async def reificate_uri_list(kernel, chain_uris, t_id):
    fdb = kernel.get_dep(Dependencies.FEDERATED_DB)
    list_ob = list()
    for uri_str in chain_uris:
        ob = await fdb.uri_read_str(t_id, uri_str)
        list_ob.append(ob)
    return list_ob


async def find_first_common_parent(kernel, left_family, right_family, t_id):
    left_chain = list()
    right_chain = list()
    fdb = kernel.get_dep(Dependencies.FEDERATED_DB)

    while True:
        left_chain.append(left_family)
        right_chain.append(right_family)

        left_uri = left_family().uri.unparse()
        right_uri = right_family().uri.unparse()

        if left_uri == right_uri:
            break

        new_left_family = await left_family().get_scalar('upper_family', t_id)
        new_right_family = await right_family().get_scalar('upper_family', t_id)

        if (new_left_family is None) or (new_right_family is None):
            raise AdelphosCoreException(ECoreErrno.EINVALID_CHAIN,
              f"Invalid chain requested: unreacheable")

        left_family = await fdb.uri_read_str(t_id, new_left_family)
        right_family = await fdb.uri_read_str(t_id, new_right_family)


    return (left_chain, right_chain)


async def get_family_chain_up_from_to(kernel,
                family_uri_src, family_to_ob, t_id):
    fdb = kernel.get_dep(Dependencies.FEDERATED_DB)

    family_uri_dst = family_to_ob().uri.unparse()

    chain = list()
    while family_uri_src != family_uri_dst:
        gCon.log(f"Doing iteration! {family_uri_src} != {family_uri_dst}")

        family_ob = await fdb.uri_read_str(t_id, family_uri_src,
                                           must_lock = True)
        chain.append(family_ob)
        family_uri_src = family_ob().uri.unparse()
        family_uri_src = await family_ob().get_scalar('upper_family', t_id)
        if family_uri_src is None:
            raise AdelphosCoreException(ECoreErrno.EINVALID_CHAIN,
              f"Invalid chain requested: {family_uri_dst} unreacheable")

    chain.append(family_to_ob)
    return chain


def check_editable_object(pars, ob_uri, owner_uri_str):
    session = pars['_param']
    if session.is_logged_root() == False:
        alias_uri_str = session.alias_uri_str
        if alias_uri_str != owner_uri_str:
            raise AdelphosCoreException(ECoreErrno.EDENIED,
f"Cannot modify {ob_uri.unparse()}, you are not {owner_uri_str} but {alias_uri_str}")
    else:
        root_uri = session.alias_uri
        if ob_uri.host != root_uri.host:
            raise AdelphosCoreException(ECoreErrno.EDENIED,
f"Cannot modify object, you are root of {root_uri.host} not of {ob_uri.host}")


async def get_family_uplevel(kernel, pars, t_id):
    chain = await get_family_chain_up(kernel, pars, t_id)
    return chain[-1]


async def get_alias_in_session(kernel, pars, t_id):
    alias_uri = pars['_param'].alias_uri
    fdb = kernel.get_dep(Dependencies.FEDERATED_DB)
    alias_ob = await fdb.uri_read_ob(t_id, alias_uri, only_local = True)
    return alias_ob


async def ensure_logged_alias_is_boss(family_ob, pars, t_id):
    logged_alias = pars['_param'].alias_uri.unparse()
    boss_uri = await family_ob().get_scalar('boss', t_id)
    if boss_uri != logged_alias:
        raise AdelphosCoreException(ECoreErrno.EDENIED, f"You are {logged_alias} not {boss_uri}")


async def ensure_family_not_associated(family_ob, t_id):
    upper_family = await family_ob().get_scalar('upper_family', t_id)
    if upper_family is not None:
        raise AdelphosCoreException(ECoreErrno.EALREADY_ASSOCIATED,
          f"Family {family_ob().uri} is already associated to {upper_family}")


