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
# this is the main context used by all the clients,
# either called from the web socket or by the client

from app.api.AliasApi import AliasApi

class AppCtx:

    def __init__(self, app):
        self.app = app


# the class that holds the data relative to a client
# this holds a session state for the socket.
class WebSocketContext(AppCtx):

    def __init__(self, app, websocket):
        super().__init__(app)
        self.websocket = websocket
        # the container for the logged user.

        # here the web socket publicies the APIs relative
        # to the objects.

        # this is the Alias as view from the external world.
        # It is ``myself'', the logged user.
        self.alias_api = AliasApi(self)

        # these API will share the context
        #self.place_api = PlaceApi(self)
        #self.cheque_api = ChequeApi(self)


