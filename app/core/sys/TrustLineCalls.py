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

class TrustLineCalls:

    @staticmethod
    @active_login
    async def _sys_call_create(kernel, session, pars):
        family_uri = session.family_uri
        pars['family_from'] = family_uri
        gCon.log(f"You want to create a trust line from {family_uri}")
        gCon.log(f"pars {pars}")
        await TrustLineCalls.tl_create_safe(kernel, pars)


    @staticmethod
    @federated_transaction(raise_if_fail = True)
    async def tl_create_safe(kernel, pars, t_id):

        fdb = kernel.get_dep(Dependencies.FEDERATED_DB)

        family_to_uri = fdb.parse_uri(pars['family_to'])
        gCon.log(f"family to uri {family_to_uri}")

        tl_name = pars['family_from'].name + "_" + \
                family_to_uri.name + "_" + \
                family_to_uri.host
        tl_name = re.sub(r'\.', "_", tl_name)
        gCon.log(f"tl name is {tl_name}")

        tl_uri = AdelphosUri.create_uri(EAdelphosType.TRUST_LINE_TYPE,
                        tl_name, host_part = pars['family_from'].host)

        gCon.log(f"the trust line uri is {tl_uri}")

        trust_line_ob = await fdb.uri_read_ob(t_id, tl_uri,
                            must_lock = True, maybe = True, only_local = True)
        if trust_line_ob is not None:
            raise AdelphosCoreException(ECoreErrno.ETL_EXISTS,
                                        tl_name)

        family_to_ob   = await fdb.uri_read_ob(t_id, family_to_uri,
                                           must_lock = True, maybe = True)

        if family_to_ob is None:
            raise AdelphosCoreException(ECoreErrno.EFAMILY_NOT_FOUND,
                                        pars['family_to'])

        trust_line_ob = await fdb.new_ob_uri(t_id, tl_uri, fields = {
            'trust' : tutils.abs_to_db(pars['trust']),
            'change_ratio' : pars['change_ratio'],
            })

        gCon.log(f"Created the trust line {trust_line_ob}")

        family_from_ob = await fdb.uri_read_ob(t_id, pars['family_from'],
                                           must_lock = True)

        trust_line_ob().set_link('family_from', family_from_ob)
        trust_line_ob().set_link('family_to', family_to_ob)

        gCon.log(f"Now the trust line has ref {trust_line_ob().ob.fields}")

        

 
