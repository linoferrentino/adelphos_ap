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
            self.instance.db.commit()
            return res 
        except AdelphosCoreException as ex:
            traceback.print_exc()
            self.instance.db.rollback()
            return -ex.errno
        except Exception as exc:
            traceback.print_exc()
            return -EAdErrno.ESYS

    return internal_commit


