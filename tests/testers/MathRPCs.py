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


from app.federation.social.SocialRPC import SocialRPC
from app.logging import gCon


class MathRPCs:


    @staticmethod
    async def radd_handler(kernel, pars):
        n1 = int(pars['n1'])
        n2 = int(pars['n2'])
        ans = n1 + n2
        return str(ans)


    @classmethod
    def get_rpcs(cls):
        return [
                SocialRPC('radd', MathRPCs.radd_handler,  ['n1', 'n2']),
                SocialRPC('pow', None,  ['base', 'exponent']),
                ]

