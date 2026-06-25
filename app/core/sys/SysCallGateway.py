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
from app.cli.CliParser import CliParser

from app.logging import gCon
import app.misc.utils as misc
from app.sdc.Dependency import Dependency
from app.federation.LifespanAware import LifespanAware
from app.federation.SyncLifespanAware import SyncLifespanAware

from app.cli.SysCall import SysCall
from app.cli.SysCall import SysCallPar



class SysCallGateway(Dependency, SyncLifespanAware):


    def __init__(self, vhost, realm = None):
        super().__init__(vhost)
        self.contexts = dict()
        self.realm = realm


    def init_syscalls(self, syscall_type):
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


    #def _add_syscalls_old(self, syscalls_list):
    #    if hasattr(self, 'syscalls') == False:
    #        self.syscalls = dict()
    #    self.syscalls = self._transform_list(syscalls_list, self.syscalls)


    async def sys_call_gateway_msg(self, param, msg):
        cp = CliParser(msg)
        ctx_cmd = cp.cmd.split('.')
        if len(ctx_cmd) != 2:
            raise AdelphosException(AdErrno.EINVALID_SYNTAX,
                                    f"{cp.cmd} not understood.")
        (context, cmd) = ctx_cmd
        gCon.log(f"Searching cmd {cmd} and context {context}")
        syscall = self.get_syscall(context, cmd)
        if syscall is None:
            raise AdelphosException(AdErrno.ENOSUCH_SYSCALL,
                                    f"{context}.{cmd}, no such command.")
        kernel = self.vhost
        kwargs = self._create_params_dict_from_cmd_line(cp, syscall)


        msg_out = await syscall.handler(kernel, param, kwargs)
        return msg_out


    @staticmethod
    def _create_params_dict_from_cmd_line(cp, syscall):
        kwargs = dict()
        gCon.log(f"I have the syscall {syscall}")
        for par in syscall.pars:
            try:
                kwargs[par.name] = cp.get_param_safe(par.name)
            except:
                if par.required:
                    raise
                else:
                    default_value = par.def_value
                    kwargs[par.name] = default_value

        gCon.log(f"the dictionary is now {kwargs}")
        return kwargs


    @staticmethod
    def _get_pars(provider):
        par_list = list()
        gCon.log(f"provider {provider}")
        for par_name, value in provider['pars'].items():
            required = value['required']
            default_value = None
            if required == False:
                default_value = value.get('default_value')
            par = SysCallPar(par_name, required, default_value)
            par_list.append(par)
        return par_list


    @staticmethod
    def _create_syscalls_list(provider_class, provider):

        syscall_list = list()
        for syscall in provider['syscalls']:
            name = syscall['name']
            if syscall.get('handler') is not None:
                handler_str = syscall['handler']
            else:
                handler_str = f'_sys_call_{name}'

            try:
                handler = getattr(provider_class, handler_str)
            except AttributeError:
                raise Exception(f"Invalid handler {handler_str}")

            pars_list = SysCallGateway._get_pars(syscall)
            syscall = SysCall(name, handler, pars_list)
            syscall_list.append(syscall)
        return syscall_list


    def register_syscalls(self, kernel, realm):

        config = kernel.conf()
        syscalls_providers = config.get_conf(realm)

        syscalls = list()

        for context, provider in syscalls_providers.items():
            gCon.log(f"adding {provider} for context {context}")

            provider_class_str = provider['class']
            provider_class = misc.import_string(provider_class_str)
            syscalls = SysCallGateway._create_syscalls_list(provider_class, provider)
            gCon.log(f"here are the syscalls {syscalls}")
            self._add_syscalls(context, syscalls)


    def clear_syscalls(self):
        self.contexts = dict()


    def _add_syscalls(self, context, syscalls):
        if self.contexts.get(context) is not None:
            raise Exception(f"Context {context} already existing")
        #gCon.log(f"Adding the context {context}")
        syscall_map = self._transform_list(syscalls)
        self.contexts[context] = syscall_map


    def get_syscall(self, context, cmd):
        rpcs = self.contexts.get(context)
        if rpcs is None:
            raise Exception(f"unknonw context to run {context}")
        rpc = rpcs.get(cmd)
        if rpc is None:
            raise Exception(f"No such remote call {context}/{rpc}")
        return rpc


    def start_sync(self):
        self.register_syscalls(self.vhost, self.realm)


    def stop_sync(self):
        self.clear_syscalls()

