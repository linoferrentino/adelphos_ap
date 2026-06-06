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


from app.federation.BackdoorRouter import BackdoorRouter


class NullNet(BackdoorRouter):
    

    def __init__(self, vhost):
        super().__init__(vhost)


