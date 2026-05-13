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


from app.transport.async_mode.StarletteWrap import StarletteWrap

from app.logging import gCon


def starlette_app_creator(routable):
    app = StarletteWrap(routable = routable)
    return app


 
