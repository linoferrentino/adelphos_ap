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


from app.sdc.Dependencies import Dependencies
from app.exc.AdelphosException import AdelphosException
from app.exc.AdelphosException import AdErrno


class SysCallGateway:


    def _add_syscalls(self, syscall_type):
        self.syscalls = dict()
        kernel = self.vhost.get_dep(Dependencies.KERNEL)
        if kernel is None:
            raise Exception("No kernel to run.")

        syscalls = kernel.get_syscalls(syscall_type)
        for sc in syscalls:
            if sc.name in self.syscalls:
                raise Exception(f"Duplicated syscall {sc.name}")
            self.syscalls[sc.name] = sc


    async def sys_call_gateway(self, session, pars):
        cmd = pars.cmd
        syscall = self.syscalls.get(cmd)
        if syscall is None:
            raise AdelphosException(AdErrno.ENOSUCH_SYSCALL,
                                    f"{cmd}, no such command.")
        msg_out = await syscall.method(syscall.self_instance, session, pars)
        return msg_out


