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

from app.core.EAdErrno import ECoreErrno
from app.core.AdelphosCoreException import AdelphosCoreException

class AliasCalls:


    @staticmethod
    async def _sys_call_alias_create(kernel, session, pars):
        alias_name = pars['name']
        password = pars['password']
        alias_splits = alias_name.split('.')
        if len(alias_splits) != 2:
            raise AdelphosCoreException(ECoreErrno.EINVALID_ALIAS_SYNTAX, alias_name)
        (alias, family) = alias_splits
        algo = kernel.get_dep(Dependencies.ALGO)

        algo.alias_algo.alias_create()

        

