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

from app.api.Gateway import Gateway
from app.api.AliasApi import AliasApi
from app.api.RootApi import RootApi
from app.api.TrustLineApi import TrustLineApi
import shlex
from abc import ABC
from app.api.AdelphosException import AdelphosException
from app.api.UserSession import UserSession
from abc import abstractmethod
from app.logging import gCon
import asyncio
import traceback


# the web socket Gateway

# the class that holds the data relative to a client
# this holds a session state for the socket.
class WebSocketGateway(Gateway):

    def __init__(self, app, websocket):
        super().__init__(app)
        self.websocket = websocket
        # the container for the logged user.

        # here the web socket publicies the APIs relative
        # to the objects.

        # this is the Alias as view from the external world.
        # It is ``myself'', the logged user.
        self.tl_api = TrustLineApi(self)
        self.alias_api = AliasApi(self)
        # the commands which only a super user can give.
        self.root_api = RootApi(self)

        # these API will share the context
        #self.place_api = PlaceApi(self)
        #self.cheque_api = ChequeApi(self)

        # the class has the ability to store a session, because we are ``talking''
        # to a user.
        self.session = UserSession(self)


    # here it is trivial, but it must return a None as a result code
    # because we want the process to be synchronously
    async def pre_process_request(self, request):
        return (None, str(request))


    # also the outgress is trivial
    async def outgress_result(self, result):
        await self.websocket.send_text(result)
