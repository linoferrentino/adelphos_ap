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
from argon2 import PasswordHasher
from app.logging import gCon
from app.core.model.AdelphosUri import EAdelphosType
from app.core.model.AdelphosUri import AdelphosUri
import app.misc.utils as misc
from app.core.ECoreErrno import ECoreErrno
from app.core.AdelphosCoreException import AdelphosCoreException


async def alias_ob_get_your_family(kernel, alias_ob, t_id):
    fdb = kernel.get_dep(Dependencies.FEDERATED_DB)
    family_uri = AdelphosUri(EAdelphosType.FAMILY_TYPE,
            alias_ob().uri.family, host = alias_ob().uri.host)
    family_ob = await fdb.uri_read_ob(t_id, family_uri,
                                      must_lock = True)
    return family_ob


async def alias_get_your_family(kernel, alias_uri_str, t_id):
    fdb = kernel.get_dep(Dependencies.FEDERATED_DB)
    alias_uri = fdb.parse_uri(alias_uri_str)
    family_uri = AdelphosUri(EAdelphosType.FAMILY_TYPE,
            alias_uri.family, host = alias_uri.host)
    family_ob = await fdb.uri_read_ob(t_id, family_uri,
                                      must_lock = True)
    return family_ob


async def alias_get_from_uri(kernel, alias_uri, t_id):
    fdb = kernel.get_dep(Dependencies.FEDERATED_DB)
    alias_ob = await fdb.uri_read_ob(t_id, alias_uri,
                                      must_lock = True)
    return alias_ob


async def _session_login(kernel, session, alias_family, password, t_id,
                         force = False):
    (alias, family) = misc.split_alias(alias_family)
    pars = {
      'alias' : alias,
      'family' : family,
      'password': password,
      'force' : force,
    }
    alias_ob = await _login_impl(kernel, pars, t_id)
    actor_handle = await alias_ob.get_scalar('actor_handle', t_id)
    social_dao = kernel.get_dep(Dependencies.SOCIAL_DAO)
    actor_dto = social_dao.actor_get_from_actor_handle(actor_handle)
    token = session.login_start(alias, family, actor_dto, alias_ob,
                                force)

    if force == True:
        return

    social = kernel.get_dep(Dependencies.SOCIAL)
    await social.out_msg_listener_to_actor(actor_dto,
      f"Copy this command to finalize login \n'alias.put_token tk {token}'")


async def _login_impl(kernel, pars, t_id):
    alias = pars['alias']
    family = pars['family']
    password = pars['password']
    force = pars['force']

    alias_uri = AdelphosUri(EAdelphosType.ALIAS_TYPE, alias, family = family)
    fdb = kernel.get_dep(Dependencies.FEDERATED_DB)

    alias_ob = await fdb.uri_read_no_lock(t_id, alias_uri, True)

    if alias_ob is None:
        raise AdelphosCoreException(ECoreErrno.EINVALID_USER_OR_PASSWORD,
                                    f"{alias}.{family}")

    if force == False:
        password_hashed = await alias_ob().get_scalar('password', t_id)

        ph = PasswordHasher()
        try:
            res = ph.verify(password_hashed, password)
        except:
            raise AdelphosCoreException(
                    ECoreErrno.EINVALID_USER_OR_PASSWORD,
                                    f"{alias}.{family}")

    return alias_ob().detach()


async def _alias_add_in_family(fdb, family_ob, user_handle,
                               name, family, password, t_id, *,
                already_hashed = False):

    if already_hashed == True:
        pass_hashed = password
    else:
        ph = PasswordHasher()
        pass_hashed = ph.hash(password)

    fields = {
            'actor_handle' : user_handle,
            'password': pass_hashed,
    }

    gCon.log(f"Adding alias {fields}")

    alias_uri = AdelphosUri(EAdelphosType.ALIAS_TYPE, name,
                            family = family)

    is_present_alias = fdb.is_present_local_uri(t_id, alias_uri)
    if is_present_alias:
        raise AdelphosCoreException(ECoreErrno.EDUPLICATED_ALIAS_IN_FAMILY,
                        f"alias {name} already present in {family}")

    alias_ob = fdb.new_ob_uri(t_id, alias_uri, fields = fields)

    family_ob().add_link('members', alias_ob)
    return alias_ob

