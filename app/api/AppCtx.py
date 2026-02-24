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

# The application context holds the transient data to fulfill a request
# or an interactive session with a client.
class AppCtx:


    # the application context has in common the Alias API.
    # only this because all the others are used by the WebSocket
    def __init__(self, app):
        self.app = app
        # the flag is used to know if we later commit or not
        self.in_error = False
        self.alias_api = AliasApi(self)


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


