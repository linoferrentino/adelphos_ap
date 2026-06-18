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


import json
import base64

from abc import ABC, abstractmethod

from app.ad_api.SocialApiProvider import SocialApiProvider
from app.cli.CliParser import CliParser
from app.cli.SysCall import SysCall
from app.core.sys.SysCallGateway import SysCallGateway
from app.exc.AdelphosException import AdErrno
from app.exc.AdelphosException import AdelphosException
from app.logging import gCon
from app.sdc.Dependencies import Dependencies

from app.misc.WrapInt import WrapInt
import asyncio

SOCIAL_API_QUERY  = "sapi.q"
SOCIAL_API_ANSWER = "sapi.a"


class AsyncCtx:

    def __init__(self, social, social_user, host, query_txt):
        self.social = social
        self.social_user = social_user
        self.host = host
        self.query_txt = query_txt
        self.async_cond = asyncio.Condition()
        self.async_ctx = asyncio.create_task(AsyncCtx.daemon_query_task(self))
        self.answer = None


    async def daemon_query_task(self):
        gCon.log(f"sending message {self.query_txt}")
        try:
            remote_user = f"@{self.social_user}@{self.host}"
            await self.social.outgoing_message(self.social_user,
                    remote_user, self.query_txt)
        except AdelphosException as adex:
            gCon.log(f"adex {adex}")
        except Exception as exc:
            gCon.log(f"generic ex {exc}")


    async def wait_until_done(self):
        gCon.log("wait!")
        while self.answer is None:
            async with self.async_cond:
                await self.async_cond.wait()


class BaseSocialApiProvider(SocialApiProvider, SysCallGateway):

    def __init__(self, vhost):
        super().__init__(vhost)
        self.contexts = dict()
        self.remote_api_id = WrapInt()
        self.async_contexts = dict()


    async def remote_req(self, context, cmd, host, **kwargs):
        rpcs = self.contexts.get(context)
        if rpcs is None:
            raise Exception(f"unknonw context to run {context}")

        is_enabled = self._is_allowed_remote_rpc_host(host, 'q')
        if is_enabled == False:
            raise AdelphosException(AdErrno.EREMOTE_ADELPHOS_UNAUTHORIZED, host)

        rpc = rpcs.get(cmd)
        if rpc is None:
            raise Exception(f"No such remote call {context}/{rpc}")

        gCon.log(f"found the syscall {rpc}")
        self._check_params(rpc, kwargs)
        msg = self._pack_request_message(cmd, kwargs)
        gCon.log(f"Sending payload -> {msg}")
        res = await self._make_rpc_request(host, msg)
        return res


    async def _make_rpc_request(self, host, msg):
        cur_api_id = self.remote_api_id.get_and_inc()
        query_txt = f"{SOCIAL_API_QUERY} api_id {cur_api_id} payload {msg}"
        social = self.vhost.get_dep(Dependencies.SOCIAL)
        async_ctx = AsyncCtx(social, self.get_social_user(), host, query_txt)
        self.async_contexts[int(cur_api_id)] = async_ctx
        await async_ctx.wait_until_done()
        gCon.log("Waited!")
        #return (async_ctx.answer['res'], async_ctx.answer['payload'])


    def _pack_request_message(self, command, param_dict):
        cmd_json = {
                'cmd' : command,
                'params' : param_dict
                }
        rcmd_str = json.dumps(cmd_json)
        return self._encode_daemon_message(rcmd_str)


    def _encode_daemon_message(self, message_str):
        remote_payload = base64.b64encode(message_str.encode())
        remote_payload_str = remote_payload.decode()
        return remote_payload_str


    def _check_params(self, rpc, kwargs):
        gCon.log(f"get params from {kwargs}")
        for param in rpc.required_pars:
            if param not in kwargs:
                raise Exception(f"required param {param} not provided")
        for param in kwargs:
            if param not in rpc.required_pars:
                raise Exception(f"got extra parameter {param} not required.")



    @abstractmethod
    def _is_allowed_remote_rpc_host(self, host, mode):
        return True


    def _add_context_rpcs(self, context, rpcs):
        if self.contexts.get(context) is not None:
            raise Exception(f"Context {context} already existing")
        gCon.log(f"Adding the context {context}")
        rpc_map = self._transform_list(rpcs)
        self.contexts[context] = rpc_map


    async def start_async(self):
        social_user = self.get_social_user()
        gCon.log(f"{id(self)} ============= START ASYNC with user {social_user}")
        social = self.vhost.get_dep(Dependencies.SOCIAL)
        social.add_listener(social_user, self)
        gCon.log(f"Registered user {social_user}")

        self.init_syscalls('social')
        syscalls = [
                SysCall(SOCIAL_API_QUERY, BaseSocialApiProvider._sys_call_q, self),
                SysCall(SOCIAL_API_ANSWER, BaseSocialApiProvider._sys_call_a, self),
          ]
        self._add_syscalls(syscalls)
        self._register_rpc_calls()

    
    async def stop_async(self):
        gCon.log(f"{id(self)} ============================= STOP ASYNC")
        social_user = self.get_social_user()
        social = self.vhost.get_dep(Dependencies.SOCIAL)
        social.remove_listener(social_user)
        self.contexts = dict()
        del self.syscalls


    async def _sys_call_q(self, session, pars):
        gCon.log(f"received the _sys_call_q with {pars}")
        pass


    async def _sys_call_a(self, session, pars):
        pass


    @abstractmethod
    def get_social_user(self):
        pass


    @abstractmethod
    def _register_rpc_calls(self):
        pass


    async def new_post(self, actor_from, msg):
        gCon.log(f"got msg from {actor_from} {msg}")
        cp = CliParser(msg)
        gCon.log(f"These are the params {cp}")
        await self.sys_call_gateway(None, cp)

