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
import app.core.sys.sys_calls_utils as scu
import app.core.sys.social_utils as su
import app.core.sys.task_utils as tku


class TrustLineCalls:

    @staticmethod
    @active_login
    async def _sys_call_create(kernel, session, pars):
        pass

    @staticmethod
    @federated_transaction(raise_if_fail = True)
    async def tl_create_safe(kernel, pars, t_id):
        pass

