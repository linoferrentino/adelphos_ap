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
        social = kernel.vhost.get_dep(Dependencies.SOCIAL)
        await social.outgoing_message(from_user, recipient, msg)
        return 'DONE!'


    async def _sys_call_radd(kernel, session, pars):
        host = pars.get_param_safe('host')
        n1 = pars.get_param_safe('n1')
        n2 = pars.get_param_safe('n2')
        recipient = f"@test_kernel@{host}"
        from_user = f"test_kernel"
        social = kernel.vhost.get_dep(Dependencies.SOCIAL)
        await social.outgoing_message(from_user, recipient, "radd")
        return "33"


    @staticmethod
    def get_syscalls(kernel):
          return [
                SysCall('dbg.echo', DebugModule._sys_call_echo, kernel),
                SysCall('dbg.sndpost', DebugModule._sys_call_sndpost, kernel),
                SysCall('dbg.radd', DebugModule._sys_call_radd, kernel),
          ]

