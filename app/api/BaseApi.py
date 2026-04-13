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
# This is the base class for the API in adelphos.
# An object of this class can give services either towards
# an Activity Pub endpoint or a web socket endpoint.

from app.logging import gCon
from app.api.AdelphosException import AdelphosException
from app.api.AdelphosException import EAdelhposErrno



# some APIs can be called only in debug.
def only_in_debug(func):

    async def check_debug_app(self):
        if self.gateway.kernel.is_debug() == False:
            raise AdelphosException('Only available in debug mode')
        return await func(self)
    return check_debug_app


# this is the basic class for all the APIs in the system
# the class goes hand in hand with the Gateway class.
# An instance of this class will give services to a Gateway.
class BaseApi:


    # the constructor takes the handler dictionary and it will register its services
    # to the gateway
    def __init__(self, gateway, handlers_dict):
        self.gateway = gateway

        # I have to register the handlers
        for handler_name, handler_fn in handlers_dict.items():
            gateway.add_handler(handler_name, self, handler_fn)



