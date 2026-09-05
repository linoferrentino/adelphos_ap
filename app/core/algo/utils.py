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
#

import traceback

from app.core.ECoreErrno import ECoreErrno
from app.core.AdelphosCoreException import AdelphosCoreException
from app.federation.FdbException import FdbException
import traceback

from app.logging import gCon
from app.sdc.Dependencies import Dependencies


def federated_transaction(raise_if_fail):

    def commit_or_die_maybe(func):

        async def internal_commit(kernel, pars):
            fdb = kernel.get_dep(Dependencies.FEDERATED_DB)
            t_id = fdb.begin_transaction()
            try:
                res = await func(kernel, pars, t_id)
                if ((pars.get('dry_run') is not None) and 
                    (pars['dry_run'] == True)):
                        fdb.rollback_transaction(t_id)
                        return {
                            'res' : 'operation canceled as requested',
                            'original_res' : res
                        }
                fdb.commit_transaction(t_id)
                return res if res is not None else ECoreErrno.DONE_OK
            except AdelphosCoreException as ex:
                traceback.print_exc()
                fdb.rollback_transaction(t_id)
                if raise_if_fail == False:
                    return -ex.errno
                raise ex
            except FdbException as fdbex:
                traceback.print_exc()
                fdb.rollback_transaction(t_id)
                if raise_if_fail == False:
                    return str(fdbex)
                raise AdelphosCoreException(ECoreErrno.EFDB, fdbex.out_str) from fdbex
            except Exception as exc:
                traceback.print_exc()
                fdb.rollback_transaction(t_id)
                if raise_if_fail == False:
                    return -ECoreErrno.ESYS
                raise AdelphosCoreException(ECoreErrno.ESYS, str(exc)) from exc 

        return internal_commit

    return commit_or_die_maybe



