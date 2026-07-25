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
from app.core.AdelphosCoreException import AdelphosCoreException
import app.misc.utils as misc

from app.misc.WrapInt import WrapInt
import asyncio
import traceback

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
        try:
            remote_user = f"@{self.social_user}@{self.host}"
            await self.social.outgoing_message(self.social_user,
                    remote_user, self.query_txt)
        except AdelphosException as adex:
            traceback.print_exc()
            self.answer = {
                'errno' : AdErrno.EGENERIC_USER_ERROR,
                'res' : adex,
                }
            self.answer = str(adex)
            async with self.async_cond:
                self.async_cond.notify_all()
        except Exception as exc:
            traceback.print_exc()
            self.answer = {
                'errno' : AdErrno.EGENERIC_SERVER,
                'res' : exc,
                }
            async with self.async_cond:
                self.async_cond.notify_all()
 

    async def wait_until_done(self):
        while self.answer is None:
            async with self.async_cond:
                await self.async_cond.wait()


class BaseSocialApiProvider(SocialApiProvider):

    def __init__(self, kernel):
        super().__init__(kernel)
        self.remote_api_id = WrapInt()
        self.async_contexts = dict()


    async def remote_req(self, context, cmd, host, **kwargs):

        is_enabled = self._is_allowed_remote_rpc_host(host, 'q')
        if is_enabled == False:
            raise AdelphosException(AdErrno.EREMOTE_ADELPHOS_UNAUTHORIZED, 
            f"{host} not allowed")

        rpc_api = self.kernel.get_dep(Dependencies.RPC_API)
        rpc = rpc_api.get_syscall(context, cmd)

        self._check_params(rpc, kwargs)
        msg = self._pack_request_message(context, cmd, kwargs)
        res = await self._make_rpc_request(host, msg)
        return res


    def remote_host_allow(self, host):
        social = self.kernel.get_dep(Dependencies.SOCIAL)
        local_user = social.local_user_get(self.get_social_user())
        user_tag_str = local_user.actor_dto.act.tag

        if user_tag_str is None:
            user_tag = {
                    'social_api' : {
                        'hosts_allow' : [host,],
                    }
            }
        else:
            user_tag = json.loads(user_tag_str)
            social_api_cnf = user_tag.get('social_api')
            if social_api_cnf is None:
                hosts_allowed_list = [host,]
            else:
                hosts_allowed_set = set(user_tag['social_api']['hosts_allow'])
                hosts_allowed_set.add(host)
                hosts_allowed_list = list(hosts_allowed_set)
            user_tag['social_api']['hosts_allow'] = hosts_allowed_list
        new_tag_str = json.dumps(user_tag)
        gCon.log(f"The new tag is {new_tag_str}")
        local_user.actor_dto.act.tag = new_tag_str
        social_dao = self.kernel.get_dep(Dependencies.SOCIAL_DAO)
        social_dao.actor_store(local_user.actor_dto)


    def remote_host_deny(self, host):
        pass


    async def _make_rpc_request(self, host, msg):
        cur_api_id = self.remote_api_id.get_and_inc()
        query_txt = f"{SOCIAL_API_QUERY} api_id {cur_api_id} payload {msg}"
        social = self.kernel.get_dep(Dependencies.SOCIAL)

        async_ctx = AsyncCtx(social, self.get_social_user(), host, query_txt)
        self.async_contexts[int(cur_api_id)] = async_ctx

        await async_ctx.wait_until_done()

        remote_errno = async_ctx.answer['errno'] 
        if remote_errno != AdErrno.DONE_OK:
            raise AdelphosException(remote_errno, async_ctx.answer['res'])
        
        if async_ctx.answer['res'] is None:
            raise AdelphosException(AdErrno.ENODATA)

        return async_ctx.answer['res']


    def _pack_request_message(self, context, command, param_dict):
        cmd_json = {
                'context' : context, 
                'cmd' : command,
                'params' : param_dict
                }
        rcmd_str = json.dumps(cmd_json)
        return self._encode_daemon_message(rcmd_str)


    def _pack_response_message(self, errno, res):
        res_json = {
                'errno' : errno,
                'res' : res,
                }
        res_str = json.dumps(res_json)
        return self._encode_daemon_message(res_str)


    def _encode_daemon_message(self, message_str):
        remote_payload = base64.b64encode(message_str.encode())
        remote_payload_str = remote_payload.decode()
        return remote_payload_str


    def _decode_daemon_message(self, daemon_str):
        remote_payload_b = base64.b64decode(daemon_str.encode())
        remote_payload_str = remote_payload_b.decode()
        return remote_payload_str


    def _check_params(self, rpc, kwargs):

        for param in rpc.pars:
            if param.name not in kwargs:
                if param.required == True:
                    raise Exception(f"required param {param} not provided")
                else:
                    kwargs[param.name] = param.def_value


    @abstractmethod
    def _is_allowed_remote_rpc_host(self, host, mode):
        return True


    def _add_context_rpcs(self, context, rpcs):
        if self.contexts.get(context) is not None:
            raise Exception(f"Context {context} already existing")
        rpc_map = self._transform_list(rpcs)
        self.contexts[context] = rpc_map


    async def start_async(self):
        social_user = self.get_social_user()
        social = self.kernel.get_dep(Dependencies.SOCIAL)
        social.add_listener(social_user, self)

    
    async def stop_async(self):
        social_user = self.get_social_user()
        social = self.kernel.get_dep(Dependencies.SOCIAL)
        social.remove_listener(social_user)


    def _check_actor_identity(self, actor_from, mode):
        allowed = self._is_allowed_remote_rpc_host(actor_from.srv.host_name, mode)
        if allowed == False:
            raise AdelphosException(EAdErrno.EREMOTE_ADELPHOS_UNAUTHORIZED)
        if actor_from.act.preferred_username != self.get_social_user():
            raise AdelphosException(EAdErrno.EREMOTE_ADELPHOS_UNAUTHORIZED)


    async def _sys_call_q(kernel, envelope, pars):
        actor_from = envelope.actor_from

        self = kernel.get_dep(Dependencies.SOCIAL_API)
        self._check_actor_identity(actor_from, 'proc')

        api_id = pars['api_id']
        try:
            res = await self._sys_call_q_try(actor_from, pars)
            remote_errno = AdErrno.DONE_OK
        except AdelphosException as adex:
            res = str(adex)
            remote_errno = adex.errno
        except Exception as exc:
            res = str(exc)
            traceback.print_exc()
            remote_errno = AdErrno.EREMOTE_ADELPHOS_ERROR

        payload_ans = self._pack_response_message(remote_errno, res)
        answer_msg = f"{SOCIAL_API_ANSWER} api_id {api_id} payload {payload_ans}"
        return answer_msg


    async def _sys_call_q_try(self, actor_from, pars):
        payload_str = pars['payload']
        payload_decoded = self._decode_daemon_message(payload_str)
        req_json = json.loads(payload_decoded)
        cmd = req_json['cmd']
        context = req_json['context']

        rpc_api = self.kernel.get_dep(Dependencies.RPC_API)
        rpc = rpc_api.get_syscall(context, cmd)

        res = await rpc.handler(self.kernel, req_json['params'])
        return res 


    async def _sys_call_a(kernel, envelope, pars):
        actor_from = envelope.actor_from

        self = kernel.get_dep(Dependencies.SOCIAL_API)
        self._check_actor_identity(actor_from, 'a')
        api_id = pars['api_id']
        payload_str = pars['payload']
        async_ctx = self.async_contexts.pop(int(api_id), None)
        if (async_ctx is None):
            raise AdelphosException(EAdErrno.EGENERIC_SERVER)
        payload_decoded = self._decode_daemon_message(payload_str)
        remote_json = json.loads(payload_decoded)
        async_ctx.answer = remote_json
        async with async_ctx.async_cond:
           async_ctx.async_cond.notify()


    @abstractmethod
    def get_social_user(self):
        pass


    async def new_post(self, envelope):
        try:
            out_msg = await self.new_post_try(envelope)
        except AdelphosCoreException as exce:
            traceback.print_exc()
            out_msg = exce.out_str
        except Exception as ex:
            traceback.print_exc()
            out_msg = f"Server Error in syscall {ex}"
    
        if out_msg is None:
            return

        social_gw = self.kernel.get_dep(Dependencies.SOCIAL_GATEWAY)
        await social_gw.out_outbox_dtos(envelope.myself,
                                        envelope.actor_from, out_msg)


    async def new_post_try(self, envelope):
        inbox_api = self.kernel.get_dep(Dependencies.INBOX_API)
        out_dict = await inbox_api.sys_call_gateway_msg(envelope, envelope.content)
        out_msg = out_dict['res']
        return out_msg

