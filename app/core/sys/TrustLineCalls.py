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

from app.core.model.AdelphosUri import AdelphosUri
from app.core.model.AdelphosUri import EAdelphosType
from app.api.UserSession import active_login
from app.core.algo.utils import federated_transaction
from app.logging import gCon
from app.sdc.Dependencies import Dependencies
from app.core.AdelphosCoreException import AdelphosCoreException
from app.core.ECoreErrno import ECoreErrno
import app.misc.trust_utils as tutils
import app.core.sys.sys_calls_utils as scu
import app.core.sys.social_utils as su
import app.core.sys.task_utils as tku


class TrustLineCalls:

    @staticmethod
    @active_login
    async def _sys_call_create(kernel, session, pars):
        pars['_session'] = session
        await TrustLineCalls.tl_create_safe(kernel, pars)


    @staticmethod
    @federated_transaction(raise_if_fail = True)
    async def tl_create_safe(kernel, pars, t_id):

        family_from_ob = await scu.get_family_in_session(kernel, pars, t_id)
        scu.ensure_logged_alias_is_boss(family_from_ob, pars)

        family_from = pars['_session'].family_uri

        fdb = kernel.get_dep(Dependencies.FEDERATED_DB)

        family_to_uri = fdb.parse_uri(pars['family_to'])
        gCon.log(f"family to uri {family_to_uri}")

        tl_name = family_from.name + "_" + \
                family_to_uri.name + "_" + \
                family_to_uri.host
        tl_name = re.sub(r'\.', "_", tl_name)
        gCon.log(f"tl name is {tl_name}")

        tl_uri = AdelphosUri.create_uri(EAdelphosType.TRUST_LINE_TYPE,
                        tl_name, host_part = family_from.host)

        gCon.log(f"the trust line uri is {tl_uri}")

        trust_line_ob = await fdb.uri_read_ob(t_id, tl_uri,
                            must_lock = True, maybe = True, only_local = True)
        if trust_line_ob is not None:
            raise AdelphosCoreException(ECoreErrno.ETL_EXISTS,
                                        tl_name)

        family_to_ob = await fdb.uri_read_ob(t_id, family_to_uri,
                                   must_lock = True, maybe = True)

        if family_to_ob is None:
            raise AdelphosCoreException(ECoreErrno.EFAMILY_NOT_FOUND,
                                        pars['family_to'])

        boss_to = family_to_ob().get_scalar('boss')

        boss_ob = await fdb.uri_read_str(t_id, boss_to, must_lock = True)

        await tku.add_task_to_alias_str(kernel, boss_ob,
                "TASK: accept_trust_family", t_id)

        await su.out_msg_to_alias_ob(kernel, boss_ob, f"""
You have received an invite to join family {family_from} by its boss
{family_from_ob().get_scalar('boss')} with a trust of 
{pars['trust']}. Login to adelphos to accept it.""", t_id)
 

