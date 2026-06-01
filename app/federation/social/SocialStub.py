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


from app.federation.SimpleSocial import SimpleSocial


class SocialStub(SimpleSocial):

    def __init__(self, vhost):
        super().__init__(vhost)


    def _create_user(self, server, user):
        pass

