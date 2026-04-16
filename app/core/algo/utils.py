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

from app.core.EAdErrno import EAdErrno
from app.core.AdelphosCoreException import AdelphosCoreException
import traceback

# decorator to do the commit fence.
def commit_or_errno(func):

    def internal_commit(self, *kwargs):
        try:
            res = func(self, *kwargs)
            self.instance.fdb.commit()
            return res 
        except AdelphosCoreException as ex:
            #traceback.print_exc()
            self.instance.fdb.rollback()
            return -ex.errno
            raise
        except Exception as exc:
            traceback.print_exc()
            self.instance.fdb.rollback()
            return -EAdErrno.ESYS
            raise

    return internal_commit


# decorator to commit only in case of success,
# rollback otherwise.
def commit_or_raise(func):

    def internal_commit(self, *kwargs):
        try:
            res = func(self, *kwargs)
            self.instance.fdb.commit()
            return res 
        except Exception as exc:
            traceback.print_exc()
            self.instance.fdb.rollback()
            # re raise!
            raise

    return internal_commit


