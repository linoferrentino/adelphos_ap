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


