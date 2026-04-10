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

import shlex
import asyncio
import traceback
import json

from abc import ABC
from abc import abstractmethod

from app.api.Gateway import Gateway
from app.api.AliasApi import AliasApi
from app.api.RootApi import RootApi
from app.api.TrustLineApi import TrustLineApi
from app.api.TestApi import TestApi

from app.api.AdelphosException import AdelphosException
from app.api.UserSession import UserSession
from app.api.OutgressGateway import post_to_ap_actor
from app.logging import gCon

# the web socket Gateway

# the class that holds the data relative to a client
# this holds a session state for the socket.
class WebSocketGateway(Gateway):


    def __init__(self, app, websocket):
        super().__init__(app)
        self.websocket = websocket

        self.alias_api = AliasApi(self)
        self.tl_api = TrustLineApi(self)
        self.root_api = RootApi(self)
        
        if app.is_test_instance():
            self.test_api = TestApi(self)

        # the container for the logged user.
        self.session = UserSession(self)
        # the super user can impersonate different identities.
        self.sessions = dict()
        self.pushed_user = None


    async def post_to_logged_user_inbox(self, msg):
        await post_to_ap_actor(self.app,
                               self.session.server_dto, self.session.actor_dto, msg)


    async def pop_user(self):

        if self.pushed_user is None:
            raise AdelphosException("No user to pop to")
        self.session = self.pushed_user


    async def push_user(self, user):

        if self.pushed_user is not None:
            raise AdelphosException("Cannot push two times")

        self.pushed_user = self.session
        
        if (user_store := self.sessions.get(user)):
            gCon.log(f"sudo user {user_store}")
            self.session = user_store
            return

        # I create a new user.
        #gCon.log(f"Create a new session for user {user}")
        self.session = UserSession(self)
        self.sessions[user] = self.session
        return await self.alias_api.force_login(user)


    # here it is trivial, but it must return a None as a result code
    # because we want the process to be synchronously
    async def pre_process_request(self, request):
        return (None, str(request))


    async def outgress_result(self, payload):
        await self.websocket.send_text(payload)
