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
from app.logging import gCon
from app.cli.CliParser import CliParser
from app.sdc.Dependencies import Dependencies
from app.core.sys.SysCallGateway import SysCallGateway
from app.cli.SysCall import SysCall
from app.exc.AdelphosException import AdelphosException
from app.exc.AdelphosException import AdErrno


class BaseSocialApiProvider(SocialApiProvider, SysCallGateway):

    def __init__(self, vhost):
        super().__init__(vhost)
        self.contexts = dict()


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

        #method_to_call = f"{cmd}_proxy"
        #try:
        #    pfnc = getattr(rpc.class_instance, method_to_call)
        #except AttributeError:
        #    raise Exception(f"remote proxy call not found for command {cmd}")

        #kernel = self.vhost.get_dep(Dependencies.KERNEL)
        #res = await pfnc(kernel, kwargs)


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
                SysCall('sapi.q', BaseSocialApiProvider._sys_call_q, self),
                SysCall('sapi.a', BaseSocialApiProvider._sys_call_a, self),
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

