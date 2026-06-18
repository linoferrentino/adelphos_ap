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


    #@staticmethod
    #async def radd_proxy(kernel, kwargs):
    #    gCon.log(f"radd_proxy get the {kwargs} kernel {kernel}")


    @staticmethod
    async def radd_handler(kernel, pars):
        pass


    @classmethod
    def get_rpcs(cls):
        return [
                SocialRPC('radd', cls,  ['n1', 'n2']),
                SocialRPC('pow', cls,  ['base', 'exponent']),
                ]

