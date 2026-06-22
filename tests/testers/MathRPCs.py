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


#from app.federation.social.SocialRPC import SocialRPC
from app.logging import gCon
from app.cli.SysCall import SysCallPar
from app.cli.SysCall import SysCall


class MathRPCs:


    @staticmethod
    async def _sys_call_radd(kernel, pars):
        n1 = int(pars['n1'])
        n2 = int(pars['n2'])
        ans = n1 + n2
        return str(ans)


    @classmethod
    def __get_rpcs(cls):
        return [
                SysCall('radd', MathRPCs.radd_handler,  [SysCallPar('n1', True),
                                                           SysCallPar('n2', True)]),
                SysCall('pow', None,  ['base', 'exponent']),
                ]

