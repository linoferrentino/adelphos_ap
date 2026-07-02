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
from app.sdc.Dependencies import Dependencies


def starlette_app_creator(kernel):
    routable = kernel.get_dep(Dependencies.ROUTER)
    app = StarletteWrap(routable = routable)
    return app


 
