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


    def init_syscalls(self, syscall_type):
        #self.syscalls = dict()
        kernel = self.vhost.get_dep(Dependencies.KERNEL)
        if kernel is None:
            raise Exception("No kernel to run.")
        syscalls_list = kernel.get_syscalls(syscall_type)
        self.syscalls = self._transform_list(syscalls_list)


    def _transform_list(self, syscalls_list, syscall_map = None):
        if syscall_map is None:
            syscall_map = dict()
        for sc in syscalls_list:
            if sc.name in syscall_map:
                raise Exception(f"Duplicated syscall {sc.name}")
            syscall_map[sc.name] = sc
        return syscall_map


    def _add_syscalls(self, syscalls_list):
        if hasattr(self, 'syscalls') == False:
            self.syscalls = dict()
        self.syscalls = self._transform_list(syscalls_list, self.syscalls)


    async def sys_call_gateway(self, param, pars):
        cmd = pars.cmd
        syscall = self.syscalls.get(cmd)
        if syscall is None:
            raise AdelphosException(AdErrno.ENOSUCH_SYSCALL,
                                    f"{cmd}, no such command.")
        msg_out = await syscall.method(syscall.self_instance, param, pars)
        return msg_out


