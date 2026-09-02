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

from app.logging import gCon

async def get_family_str_in_session(kernel, pars, t_id):
    family_uri = pars['_session'].family_uri
    return family_uri.unparse()


async def get_family_in_session(kernel, pars, t_id):
    family = pars['_session'].family
    fdb = kernel.get_dep(Dependencies.FEDERATED_DB)
    family_uri = AdelphosUri(EAdelphosType.FAMILY_TYPE, family)
    family_ob = await fdb.uri_read_ob(t_id, family_uri, must_lock = True,
                                      only_local = True)
    return family_ob


async def get_family_source(kernel, pars, t_id):
    family_source = pars.get('family_source')
    if family_source is None:
        family_ob = await get_family_in_session(kernel, pars, t_id)
        pars['family_source'] = pars['_session'].family_uri.unparse()
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
    chain = list()
    fdb = kernel.get_dep(Dependencies.FEDERATED_DB)
    family_ob = await get_family_in_session(kernel, pars, t_id)
    uplevel = pars['uplevel']
    chain.append(family_ob)
    for lev in range(0, uplevel):
        family_uri = family_ob().get_scalar('upper_family')
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
        family_uri_src = family_ob().get_scalar('upper_family')
        if family_uri_src is None:
            raise AdelphosCoreException(ECoreErrno.EINVALID_CHAIN,
              f"Invalid chain requested: {family_uri_dst} unreacheable")

    chain.append(family_to_ob)
    return chain


async def get_family_uplevel(kernel, pars, t_id):
    chain = await get_family_chain_up(kernel, pars, t_id)
    return chain[-1]


async def get_alias_in_session(kernel, pars, t_id):
    alias_uri = pars['_session'].alias_uri
    fdb = kernel.get_dep(Dependencies.FEDERATED_DB)
    alias_ob = await fdb.uri_read_ob(t_id, alias_uri, must_lock = True,
                                     only_local = True)
    return alias_ob


def ensure_logged_alias_is_boss(family_ob, pars):
    logged_alias = pars['_session'].alias_uri.unparse()
    boss_uri = family_ob().get_scalar('boss')
    if boss_uri != logged_alias:
        raise AdelphosCoreException(ECoreErrno.EDENIED, f"You are {logged_alias} not {boss_uri}")


def ensure_family_not_associated(family_ob):
    upper_family = family_ob().get_scalar('upper_family')
    if upper_family is not None:
        raise AdelphosCoreException(ECoreErrno.EALREADY_ASSOCIATED,
          f"Family {family_ob().uri} is already associated to {upper_family}")


