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
from app.api.TrustLineApi import TrustLineApi
import shlex
from abc import ABC
from abc import abstractmethod
from app.logging import gCon
import asyncio

# The application context holds the transient data to fulfill a request
# or an interactive session with a client.

# this will be renamed in ApplicationGateway
# the gateway to access the adelphos instance, using either an
# ActivityPub post message or a web socket.
# The Gateway is stateful, but an ActivityPub Gateway will be discarded after use.
# the gateway has a set of APIs to control the system
class AppCtx(ABC):


    # the application context has in common the Alias API.
    # only this because all the others are used by the WebSocket
    def __init__(self, app):
        self.app = app
        # the flag is used to know if we later commit or not
        self.in_error = False
        # the AliasApi is in common between the two gateways as we create an
        # alias using the ActivityPub interface and we access the web socket
        # using the alias created with activity pub
        self.alias_api = AliasApi(self)


    # the gateway has this entry point common to all.
    # the request could be ``anything'', for an ActivityPub Gateway it
    # is a request, for a socket it is a line of text.
    async def new_request(self, request):

        # at the beginning I do not have an async request (or I delete the previous one) 
        self.async_ctx = None

        # this pre process can have two outcomes
        # a status code and a string, in this case the status code
        # is given immediately to the outside and the request as string
        # is fed as a new task (if it is != None)
        # otherwise the status code is None, in this case the request is
        # processed serially.
        (res_code, req_str) = await self.pre_process_request(request)

        if (res_code is None):
            # this is a serialized request, the output is the response
            response = await self.proc_request(req_str)
        else:
            # this is a request that needs to be processed in another thread, and
            # the return is the res_code
            response = res_code
            if (req_str is not None):
                gCon.log(f"Creating task for request -{req_str}-")
                asyncio.create_task(self.proc_request(req_str))

        # this is the processing part of the request
        # the processing part of the request will then issue an outgress command.
        return response


    # the request can be anything here, a string or a HTTP request.
    @abstractmethod
    async def pre_process_request(self, request):
        pass


    # here the method is not entirely abstract, we have to return a string.
    async def proc_request(self, req_str):

        self.parse_cmd_line(req_str)

        # I have first to call the real handler, this might produce an exception!
        msg_out = await self._proc_request_impl()

        # the request could have created an async context, in this case
        # the real message will be available at the end of the async call

        # XXX maybe this wait can be moved.
        if (self.async_ctx is not None):
            msg_out = await self.async_ctx

        # OK, now I will check if there has been an exception, if not I can commit
        if (self.in_error == False):
            gCon.rule("[blue]Commit![/blue]")
            self.app.dao.commit()
        else:
            gCon.rule("[red]Rollback![/red]")
            self.app.dao.rollback()

        await self.outgress_result(msg_out)


    # this is an abstract method here, different gateways will implement it differently
    @abstractmethod
    async def outgress_result(self, result):
        pass


    # the request has been parsed, now we have only to process it
    # this should return a string which is the result or, if the request
    # is itself a result of another job it will return an async context.
    @abstractmethod
    async def _proc_request_impl(self):
        pass


    # parse the parameters: they can come either from an Activity Pub message or
    # a web socket (or a GUI client, later...)
    def parse_cmd_line(self, command_line):
        parsed_line = shlex.split(command_line)
        self.cmd = None
        self.cmd_dict = {}
        
        # the first token is the command, the other are the parameters, in key-value
        # pair
        cur_key = None
        for tk in parsed_line:
            if (self.cmd is None):
                self.cmd = tk
                continue
            if (cur_key is None):
                cur_key = tk
                continue
            # I put the value
            self.cmd_dict[cur_key] = tk
            cur_key = None


    def get_param_safe(self, param, default = None):
        par_value = self.cmd_dict.get(param)
        
        if (par_value is not None):
            return par_value

        if (default is not None):
            return default

        raise AdelphosException(f"Required parameter {param} not found and default not given")


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
        self.tl_api = TrustLineApi(self)

        # these API will share the context
        #self.place_api = PlaceApi(self)
        #self.cheque_api = ChequeApi(self)


    def proc_request(self, request):
        pass
