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


class TestKernel(Kernel):

    def __init__(self, vhost):
        super().__init__(vhost)


    async def start_async(self):
        pass


    async def stop_async(self):
        pass


    async def proc_msg(self, msg):
        host_dest = msg
        social = self.vhost.get_dep(Dependencies.SOCIAL)
        gCon.log(f"[red]send message to {host_dest} : {msg}[/red]")
        await social.outgoing_message(f"@EchoKernel@{host_dest}", "ping")
        return "DONE!"


