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
# The gateway is the entry class to Adelphos.

from app.api.AliasApi import AliasApi
from app.api.TrustLineApi import TrustLineApi
import shlex
from abc import ABC
from app.api.AdelphosException import AdelphosException
from app.api.AdelphosException import EAdelhposErrno
from abc import abstractmethod
from app.logging import gCon
import asyncio
import traceback
import json


class Gateway(ABC):


    # the application context has in common the Alias API.
    # only this because all the others are used by the WebSocket
    def __init__(self, app):
        self.app = app
        self.handlers = dict()
        self.handlers['AdelphosError'] = (self, Gateway._handle_remote_error)


    # this message is called by an handler to register its functions.
    def add_handler(self, command_str, other_self, handler):
        self.handlers[command_str] = (other_self, handler)


    # the gateway has this entry point common to all.
    # the request could be ``anything'', for an ActivityPub Gateway it
    # is a request, for a socket it is a line of text.
    async def new_request(self, request):

        # at the beginning I do not have an async request (or I delete the previous one) 
        self.async_ctx = None
        self.in_error = False

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
                #gCon.log(f"Creating task for request -{req_str}-")
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

        self.parse_request_string(req_str)

        # I have first to call the real handler, this might produce an exception!
        (errno, msg_clear) = await self.proc_request_try()

        # the request could have created an async context, in this case
        # the real message will be available at the end of the async call

        # OK, now I will check if there has been an exception, if not I can commit
        if (self.in_error == False):
            #gCon.log("[blue]commit[/blue]")
            self.app.dao.commit()
        else:
            #gCon.log("[red]rollback[/red]")
            self.app.dao.rollback()

        # do not ping back the error!
        payload = self.pack_message(errno, msg_clear)

        if errno != EAdelhposErrno.EREMOTE_ERROR:
            payload_encoded = self.post_process_msg(payload)
            await self.outgress_result(payload)

        # the result is given also in clear as a return value for the automating scripts
        return payload


    # this is an abstract method here, different gateways will implement it differently
    # the error code should have been already packed
    @abstractmethod
    async def outgress_result(self, result):
        pass


    # the request has been parsed, now we have only to process it
    # this should return a string which is the result or, if the request
    # is itself a result of another job it will return an async context.
    #@abstractmethod
    async def proc_request_try(self):


        try:
            msg_out = await self.proc_req_bare()
            errno = EAdelhposErrno.DONE_OK
        except AdelphosException as adex:
            gCon.log(f"USER Error {adex}")
            traceback.print_exc()
            errno = adex.code
            msg_out = f"AdelphosError in your request (you have done a mistake): {adex}"
            self.in_error = True
        except Exception as ex:
            gCon.log(f"SERVER Error {ex}")
            traceback.print_exc()
            errno = EAdelhposErrno.EGENERIC_SERVER
            msg_out = f"AdelphosError in server (this might be a bug, sorry): {ex}"
            self.in_error = True


        # some gateways will pack the message and the error together.
        #packed_message = Gateway.pack_message(errno, msg_out)
        #post_proc_msg = self.post_process_msg(packed_message)

        # here I return the simple tuple in clear
        return (errno, msg_out)


    def pack_message(self, errno, msg_out):
        if msg_out is None or len(msg_out) == 0:
            msg_out = "Done." if errno == EAdelhposErrno.DONE_OK else "Error."
        final_msg = {
                'res' : errno,
                'payload' : msg_out 
        }
        return json.dumps(final_msg)


    # This is a NOP for all but the AdelphosGateway 
    def post_process_msg(self, msg_out):
        return msg_out


    async def _handle_remote_error(self):
        # I raise a remote error to stop infinite recursion.
        raise AdelphosException("__recurse error__", EAdelhposErrno.EREMOTE_ERROR)


    async def proc_req_bare(self):

        # search for the handler for this command.
        handler_tuple = self.handlers.get(self.cmd)
        if handler_tuple is None:
            raise AdelphosException(
                    f"Not found command  {self.cmd}",
                    EAdelhposErrno.ECOMMAND_NOT_FOUND)
        msg_out = await handler_tuple[1](handler_tuple[0])
        return msg_out


    # parse the parameters: they can come either from an Activity Pub message or
    # a web socket (or a GUI client, later...)
    # Derived classes could override this method.
    def parse_request_string(self, command_line):
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


