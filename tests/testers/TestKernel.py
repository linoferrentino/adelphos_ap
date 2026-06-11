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

from app.federation.Kernel import Kernel
from app.sdc.Dependencies import Dependencies
from app.logging import gCon
from app.cli.SysCall import SysCall
from app.api.UserSession import active_login
from app.core.sys.DebugModule import DebugModule


class TestKernel(Kernel):

    def __init__(self, vhost):
        super().__init__(vhost)


    async def start_async(self):
        pass


    async def stop_async(self):
        pass


    def get_syscalls(self):
        #return [
        #        SysCall('echo', TestKernel._sys_call_echo, self),
        #        SysCall('sndpost', TestKernel._sys_call_sndpost, self),
        #        ]
        syscalls = []
        syscalls.extend(DebugModule.get_syscalls(self))
        return syscalls


    async def proc_msg_XXX(self, cp, session):

        cmd = cp.cmd

        if cmd == 'echo':
            val = cp.get_param_safe('msg')
            res = f"hello {val}!"
            return res
        elif cmd == 'sndpost':
            return 'DONE!'

        host_dest = f'@ll {cmd}'
        msg = 'llla'
        social = self.vhost.get_dep(Dependencies.SOCIAL)
        gCon.log(f"[red]send message to {host_dest} : {msg} {cp}[/red]")
        await social.outgoing_message(f"@EchoKernel@{host_dest}", "ping")
        return "DONE!"


    #@active_login
    #async def _sys_call_echo(self, session, pars):
    #    val = pars.get_param_safe('msg')
    #    res = f"hello {val}!"
    #    return res


    ##@active_login
    #async def _sys_call_sndpost(self, session, pars):
    #    recipient = pars.get_param_safe('to')
    #    msg = pars.get_param_safe('msg')
    #    from_user = pars.get_param_safe('from')
    #    #local_user = session.get_user()
    #    gCon.log(f"sending message {msg} to {recipient} from {from_user}")
    #    social = self.vhost.get_dep(Dependencies.SOCIAL)
    #    await social.outgoing_message(from_user, recipient, msg)
    #    return 'DONE!'


#SYSCALLS = {
#     'echo' : TestKernel._sys_call_echo,
#     'sndpost' : TestKernel._sys_call_sndpost,
#}


