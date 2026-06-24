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


from app.core.sys.SysCallModule import SysCallModule
from app.sdc.Dependencies import Dependencies
from app.cli.SysCall import SysCall
from app.logging import gCon


class DebugModule:


    async def _sys_call_echo(kernel, session, pars):
        val = pars.get_param_safe('msg')
        res = f"hello {val}!"
        return res


    async def _sys_call_sndpost(kernel, session, pars):
        recipient = pars.get_param_safe('to')
        msg = pars.get_param_safe('msg')
        from_user = pars.get_param_safe('from')
        gCon.log(f"sending message {msg} to {recipient} from {from_user}")
        social = kernel.get_dep(Dependencies.SOCIAL)
        await social.outgoing_message(from_user, recipient, msg)
        return 'DONE!'


    async def _sys_call_radd(kernel, session, pars):
        host = pars['host']
        n1 = pars['n1']
        n2 = pars['n2']
        social_api = kernel.get_dep(Dependencies.SOCIAL_API)
        res = await social_api.remote_req('math', 'radd', host, n1 = n1, n2 = n2)
        return res


    @staticmethod
    def get_syscalls(kernel):
          return [
                SysCall('dbg.echo', DebugModule._sys_call_echo),
                SysCall('dbg.sndpost', DebugModule._sys_call_sndpost),
                SysCall('dbg.radd', DebugModule._sys_call_radd),
          ]

