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


    def get_cli_syscalls(self):
        syscalls = []
        syscalls.extend(DebugModule.get_syscalls(self))
        return syscalls


    def get_social_syscalls(self):
        return []


