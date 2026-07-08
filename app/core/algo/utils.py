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

# decorator to do the commit fence.
#def commit_or_errno(func):
#
#    def internal_commit(self, *args, **kwargs):
#        t_id = self.kernel.fdb.begin_transaction()
#        kwargs['t_id'] = t_id
#        try:
#            res = func(self, *args, **kwargs)
#            self.kernel.fdb.commit_transaction(t_id)
#            return res 
#        except AdelphosCoreException as ex:
#            #traceback.print_exc()
#            self.instance.fdb.rollback_transaction(t_id)
#            return -ex.errno
#        except Exception as exc:
#            traceback.print_exc()
#            self.kernel.fdb.rollback_transaction(t_id)
#            return -EAdErrno.ESYS
#
#    return internal_commit
#
#
## decorator to commit only in case of success,
## rollback otherwise.
#def commit_or_raise(func):
#
#    def internal_commit(self, *args, **kwargs):
#        try:
#            res = func(self, *args, **kwargs)
#            self.instance.fdb.commit()
#            return res 
#        except Exception as exc:
#            traceback.print_exc()
#            self.instance.fdb.rollback()
#            # re raise!
#            raise
#
#    return internal_commit

from app.logging import gCon
from app.sdc.Dependencies import Dependencies


def federated_transaction(raise_if_fail = True):

    def commit_or_die_maybe(func):

        async def internal_commit(kernel, *args, **kwargs):
            fdb = kernel.get_dep(Dependencies.FEDERATED_DB)
            t_id = await fdb.begin_transaction()
            kwargs['t_id'] = t_id
            try:
                res = await func(kernel, *args, **kwargs)
                await fdb.commit_transaction(t_id)
                return res if res is not None else ECoreErrno.DONE_OK
            except AdelphosCoreException as ex:
                await fdb.rollback_transaction(t_id)
                if raise_if_fail == False:
                    return -ex.errno
                raise ex
            except FdbException as fdbex:
                traceback.print_exc()
                await fdb.rollback_transaction(t_id)
                if raise_if_fail == False:
                    return str(fdbex)
                raise AdelphosCoreException(ECoreErrno.EFDB) from fdbex
            except Exception as exc:
                traceback.print_exc()
                await fdb.rollback_transaction(t_id)
                if raise_if_fail == False:
                    return -ECoreErrno.ESYS
                raise AdelphosCoreException(ECoreErrno.ESYS) from fdbex

        return internal_commit

    return commit_or_die_maybe



