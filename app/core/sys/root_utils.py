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


from app.logging import gCon
from app.sdc.Dependencies import Dependencies
from app.core.algo.utils import federated_transaction
from app.core.ECoreErrno import ECoreErrno
from app.core.AdelphosCoreException import AdelphosCoreException
from app.core.model.AdelphosUri import AdelphosUri
from app.core.model.AdelphosUri import EAdelphosType
import app.misc.trust_utils as tutils
import app.core.sys.family_utils as fu
import app.core.sys.sys_calls_utils as scu



@federated_transaction(raise_if_fail = True)
async def build_upper_family_ob_safe(kernel, pars, t_id):
    await build_upper_family_ob_impl(kernel, pars, t_id)


async def build_upper_family_ob_impl(kernel, pars, t_id):
    boss = pars['boss']
    carrier = pars['carrier']
    level = pars['level']
    gCon.log(f"installing level {level} family {pars} it has boss {boss}")

    if level < 1:
        raise AdelphosCoreException(ECoreErrno.EWRONGLEVEL,
                        f"Upper families must have at least level 1, got {level}.")

    level_exp = level - 1

    fdb = kernel.get_dep(Dependencies.FEDERATED_DB)

    members = pars['members']
    members_ob = list()
    for member in members:
        member_ob = await fdb.uri_read_str(t_id, member)
        lev_member = await member_ob().get_scalar('level', t_id)
        if lev_member != level_exp:
            raise AdelphosCoreException(ECoreErrno.EWRONGLEVEL,
             f"family {member} has level {lev_member}, expected {level_exp}")
        members_ob.append(member_ob)

    boss_ob = await fdb.uri_read_str(t_id, boss)
    carrier_ob = await fdb.uri_read_str(t_id, carrier)

    await scu._ensure_alias_in_families(kernel, boss_ob, members, t_id)
    await scu._ensure_alias_in_families(kernel, carrier_ob, members, t_id)

    name = pars['name']
    family_uri = AdelphosUri(EAdelphosType.FAMILY_TYPE, name)

    balance = pars.get('balance', 0)
    my_trust = pars.get('my_trust', 5)
    system_trust = pars.get('system_trust', 5)

    if my_trust < 0:
        raise AdelphosCoreException(EINVALID_TRUST)

    if system_trust < 0:
        raise AdelphosCoreException(EINVALID_TRUST)

    if (balance > 0) and (balance > my_trust):
        raise AdelphosCoreException(EINSUFFICIENT_TRUST_IN_ADELPHOS,
                f"family {name} cannot have a balance more than {my_trust}")
    elif (balance < 0) and (abs(balance) > system_trust):
        raise AdelphosCoreException(EINSUFFICIENT_TRUST_FROM_ADELPHOS,
                f"family {name} cannot have a balance less than -{system_trust}")

    my_trust_db = tutils.abs_to_db(my_trust)
    system_trust_db = tutils.abs_to_db(system_trust)
    brotherhood_ratio = pars['brotherhood_ratio']
    fields = {
        'level' : level,
        'brotherhood_ratio': brotherhood_ratio,
        'my_trust' : my_trust_db,
        'system_trust' : system_trust_db,
    }
    if balance != 0:
        fields['balance'] = balance

    family_ob = fdb.new_ob_uri(t_id, family_uri, fields)

    await fu.add_default_agora(fdb, family_ob, carrier_ob, t_id)
    await family_ob().set_link('boss', boss_ob, t_id)

    for member_ob in members_ob:
        await member_ob().set_link('upper_family', family_ob, t_id)
        family_ob().add_link('members', member_ob)

