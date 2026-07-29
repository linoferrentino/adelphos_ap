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


from argon2 import PasswordHasher
from app.core.algo.utils import federated_transaction
from app.core.algo.FamilyAlgo import FamilyAlgo
from app.core.model.AdelphosUri import EAdelphosType
from app.logging import gCon
from app.core.ECoreErrno import ECoreErrno
from app.core.AdelphosCoreException import AdelphosCoreException
from app.core.model.AdelphosUri import AdelphosUri
from app.sdc.Dependencies import Dependencies
import weakref
import sys
import app.misc.alias_utils as au
import app.misc.trust_utils as tutils

from app.logging import gCon


class AliasAlgo:

    @staticmethod
    async def _sys_call_join_family(kernel, envelope, pars):
        alias = pars['alias']
        family = pars['family']
        invite_code = pars['invite_code']
        gCon.log(f"received command to join family {family}")
 

    @staticmethod
    async def _sys_call_create(kernel, envelope, pars):
        alias_name = pars['name']
        password = pars['password']
        trust = pars['trust']

        (alias, family) = au.split_alias(alias_name, True)

        await AliasAlgo.alias_create_safe(kernel, envelope.actor_from.act.actor_id,
                                     alias, family, password, trust)
        return "Alias created, you can login, now."


    @staticmethod
    @federated_transaction(raise_if_fail = False)
    async def alias_create(kernel, actor_id, name, family, password,
                           trust, t_id):
        return await AliasAlgo._alias_create_impl(kernel, actor_id, 
                        name, family, password, trust, t_id)
 

    @staticmethod
    @federated_transaction(raise_if_fail = True)
    async def alias_create_safe(kernel, actor_id, name, family, password,
                                trust, t_id):
        return await AliasAlgo._alias_create_impl(kernel, actor_id, 
                        name, family, password, trust, t_id)
 

    async def _alias_create_impl(kernel, actor_id, name,
                                 family, password, trust, t_id):

        if trust <= 0:
            raise AdelphosCoreException(ECoreErrno.EINVALID_TRUST, trust)

        fdb = kernel.get_dep(Dependencies.FEDERATED_DB)
        family_uri = AdelphosUri(EAdelphosType.FAMILY_TYPE, family)

        is_present_family = await fdb.is_present_uri_str(t_id, family_uri)

        if is_present_family is True:
            raise AdelphosCoreException(ECoreErrno.EDUPLICATED_FAMILY)

        family_ob = await fdb.new_ob_uri(t_id, family_uri, fields = {
            'trust' : tutils.abs_to_db(trust)
            })

        ph = PasswordHasher()
        pass_hashed = ph.hash(password)

        fields = {
                'actor_id' : actor_id,
                'password': pass_hashed
        }

        alias_ob = await fdb.new_ob(t_id, EAdelphosType.ALIAS_TYPE, 
                                      name, family = family, fields = fields)

        family_ob().set_link('boss', alias_ob)
        family_ob().add_link('members', alias_ob)
        

