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


class MathRPCs:


    @staticmethod
    def radd_proxy(self, n1, n2):
        pass


    @staticmethod
    def radd_stub(self, n1, n2):
        pass


    @classmethod
    def get_rpcs(cls, other_self):
        return [
                SocialRPC('radd', cls, other_self, ['n1', 'n2']),
                SocialRPC('pow', cls, other_self, ['base', 'exponent']),
                ]

