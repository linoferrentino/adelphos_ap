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

# This is the Daemon API, in Activity Pub the daemon answers to
# requests done by other adelphos daemons in the fediverse.


# this is the external daemon api, the one which uses Activity Pub as
# the transport. Inside it there is the normal API which is as if the request
# has been done locally from a web socket.

import secrets
import asyncio
import json

from app.api.BaseApi import BaseApi
from app.api.AdelphosException import AdelphosException
from app.api.AdelphosException import EAdelhposErrno
from app.logging import gCon


# the async context used to store the condition to wait for the answer
class ApAsyncContext:

    def __init__(self, gateway, ad_instance_pack, query_txt):
        self.gateway = gateway
        self.ad_instance_pack = ad_instance_pack
        self.query_txt = query_txt
        self.async_cond = asyncio.Condition()
        # I create an async thread to send the request
        self.async_ctx = asyncio.create_task(ApAsyncContext.daemon_query_task(self))
        # this will be valorized by the daemon_a handler
        self.answer = None


    async def daemon_query_task(self):

        # post the request and then wait for the response.
        await self.gateway.app.ap_api.post_to_fediverse_actor_as_daemon(
                self.ad_instance_pack.server, self.ad_instance_pack.actor, self.query_txt)


    async def wait_until_done(self):

        while self.answer is None:
            async with self.async_cond:
                await self.async_cond.wait()

        # a remote error will be a local exception.
        if (self.answer['res'] != EAdelhposErrno.DONE_OK):
            raise AdelphosException(f"remote error {self.answer}", self.answer['res'])


class ApDaemonApi(BaseApi):

    def __init__(self, gateway):
        super().__init__(gateway, HANDLERS)
    
        # I start from a random api sequence.
        self.remote_api_id = secrets.randbits(31)
        # this holds my async requests done so far.
        self.async_contexts = {}


    # here I can encode a request for the remote adelphos
    def encode_remote_response(self, api_id, response):
        answer_txt = f"daemon_a api_id {api_id} payload {response}"
        return answer_txt


    # this blocks the caller until an answer
    async def make_request(self, ad_instance_pack, request):

        cur_api_id = self.remote_api_id
        # wrap around?
        if self.remote_api_id == 0x7FFFFFFF:
            self.remote_api_id = 0
        else:
            self.remote_api_id += 1

        # I have to encode the request.
        query_txt = f"daemon_q api_id {cur_api_id} payload {request}"

        # I have to create the async context for this request
        async_ctx = ApAsyncContext(self.gateway, ad_instance_pack, query_txt)
        # I put it into the dictionary because I need to retrieve it for the response
        self.async_contexts[int(cur_api_id)] = async_ctx

        gCon.log(f"[blue]my question {self.async_contexts}[/blue]")
        # OK, now I wait for a response!
        # this will block!
        gCon.log(f"[red]Now I will wait until done![/red] {id(self)}")
        await async_ctx.wait_until_done()
        gCon.log(f"[green]Waited the msg is {async_ctx.answer}[/green]")

        if async_ctx.answer['res'] == EAdelhposErrno.DONE_OK:
            return async_ctx.answer['payload']

        # If not this is a local exception
        raise AdelphosException(async_ctx.answer['payload'],
                                async_ctx.answer['res'])



    async def _hndl_daemon_q(self):
        # here the request is unpacked in the 'normal' way, because here we
        # have still a big message
        # also in this part I have to check the authorized instance
        api_id = self.gateway.get_param_safe('api_id')
        payload_str = self.gateway.get_param_safe('payload')

        payload_ans = await self.gateway.app.ad_gateway.new_request(payload_str)
        gCon.log(f"[yellow]Payload ans {payload_ans}[/yellow]")
        response_str = self.encode_remote_response(api_id, payload_ans)
        gCon.log(f"------> response {response_str}")

        # I have to post the response to the activity pub actor which has given
        return response_str 


    async def _hndl_daemon_a(self):

        api_id = self.gateway.get_param_safe('api_id')
        payload_str = self.gateway.get_param_safe('payload')
        gCon.log(f"------> I have received {payload_str} for apiid {api_id}")
        async_ctx = self.async_contexts.pop(int(api_id), None)
        if (async_ctx is None):
            # this is an internal error, or a tentative attack?
            gCon.log(f"[blue]my question {self.async_contexts}[/blue]")
            raise AdelphosException(f"No question asked {api_id} {id(self)}",
                                    EAdelhposErrno.EGENERIC_SERVER)

        # I have to unpack the remote payload
        payload_decoded  = self.gateway.app.ad_gateway._decode_daemon_message(
                payload_str)
        remote_json = json.loads(payload_decoded)
        async_ctx.answer = remote_json
        async with async_ctx.async_cond:
           async_ctx.async_cond.notify()



HANDLERS = {
     'daemon_q' : ApDaemonApi._hndl_daemon_q,
     'daemon_a' : ApDaemonApi._hndl_daemon_a,
}

