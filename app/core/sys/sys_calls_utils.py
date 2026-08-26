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
        return await get_family_in_session(kernel, pars, t_id)
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


async def get_family_uplevel(kernel, pars, t_id):
    family_ob = await get_family_in_session(kernel, pars, t_id)
    uplevel = pars['uplevel']
    for lev in range(0, uplevel):
        family_uri = family_ob().get_scalar('upper_family')
        if family_uri is None:
            raise AdelphosCoreException(ECoreErrno.EUPLEVEL_NOT_FOUND,
                                        f"lev {lev+1} not found")
        family_ob = await fdb.uri_read_ob(t_id, family_uri, must_lock = True)
    return family_ob


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


