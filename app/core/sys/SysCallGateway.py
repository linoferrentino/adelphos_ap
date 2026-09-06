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


import re
import sys
import traceback

from app.sdc.Dependencies import Dependencies
from app.exc.AdelphosException import AdelphosException
from app.core.AdelphosCoreException import AdelphosCoreException
from app.exc.AdelphosException import AdelphosContinueException
from app.exc.AdelphosException import AdErrno
from app.core.ECoreErrno import ECoreErrno
from app.cli.CliParser import CliParser

from app.logging import gCon
import app.misc.utils as misc
from app.sdc.Dependency import Dependency
from app.federation.LifespanAware import LifespanAware
from app.federation.SyncLifespanAware import SyncLifespanAware

from app.cli.SysCall import SysCall
from app.cli.SysCall import SysCallPar



class SysCallGateway(Dependency, SyncLifespanAware):


    def __init__(self, kernel, realm = None):
        super().__init__(kernel)
        self.contexts = dict()
        self.realm = realm


    def init_syscalls(self, syscall_type):
        kernel = self.kernel.get_dep(Dependencies.KERNEL)
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


    async def sys_call_gateway_msg(self, param, msg):
        cp = CliParser(msg)
        ctx_cmd = cp.cmd.split('.')
        if len(ctx_cmd) != 2:
            raise AdelphosException(AdErrno.EINVALID_SYNTAX,
                                    f"{cp.cmd} not understood.")
        (context, cmd) = ctx_cmd
        syscall = self.get_syscall(context, cmd)
        kernel = self.kernel
        kwargs = self._create_params_dict_from_cmd_line(cp, syscall)

        return await self.sys_call_handler_call(context, syscall, param, kwargs)


    async def sys_call_handler_call(self, context, syscall, param, kwargs):
        presenter = self.kernel.get_dep(Dependencies.CLI_PRESENTER)
        try:
            msg_out = await self.sys_call_handler_call_try(
                    context, syscall, param, kwargs)
            errno = int(AdErrno.DONE_OK)
        except AdelphosContinueException as exce:
            raise
        except AdelphosCoreException as exce:
            traceback.print_exc()
            msg_out = exce.out_str
            errno = exce.errno
        except AdelphosException as exce:
            traceback.print_exc()
            errno = exce.errno
            msg_out = exce.out_str
        except Exception as ex:
            traceback.print_exc()
            errno = int(ECoreErrno.ESYS)
            msg_out = f"System exception {str(type(ex))} Details {str(ex)}"

        dict_out = {
                'errno' : errno,
                'res' : msg_out if msg_out is not None else "",
                'realm' : self.realm,
                'context' : context,
                'syscall' : syscall.name,
                }

        response_str = presenter.present_to_user_ok(dict_out)
        return response_str


    async def sys_call_handler_call_try(self, context, syscall, param, kwargs):
        kwargs['_unsafe'] = False
        msg_out = await syscall.handler(self.kernel, param, kwargs)
        return msg_out


    @staticmethod
    def _create_params_dict_from_cmd_line(cp, syscall):
        kwargs = dict()
        for par in syscall.pars:
            try:
                val_str = cp.get_and_pop_par(par.name)
                match par.par_type:
                    case 'str':
                        val_final = val_str
                    case 'bool':
                        val_final = False if (re.match('[Ff]alse',
                                val_str) is not None) else True
                    case 'float':
                        val_final = float(val_str)
                    case 'int':
                        val_final = int(val_str)
            except Exception as ex:
                if par.required:
                    raise AdelphosException(
                        AdErrno.EREQUIRED_PARAMETER_MISSING, par.name) from ex
                else:
                    val_final = par.def_value

            if par.validator is not None:
                string_validator = re.sub("_v_", str(val_final), par.validator)
                gCon.log(f"The validator is {string_validator}")
                validator_result = eval(string_validator)
                if validator_result != True:
                    raise AdelphosException(
                        AdErrno.EVALIDATOR_EXCEPTION, val_final)

            kwargs[par.name] = val_final

        if cp.npars() != 0:
            extra_pars = cp.par_list()
            gCon.log(f"[red]extra pars {extra_pars}[/red]")
            raise AdelphosException(
                AdErrno.EUNKOWN_PARAMETERS_GIVEN, f"extra pars {extra_pars}")
        return kwargs


    @staticmethod
    def _get_pars(provider):
        par_list = list()
        if provider.get('pars') is None:
            return par_list
        for par_name, value in provider['pars'].items():
            required = value['required']
            default_value = None
            if required == False:
                default_value = value.get('default')
            par_type = value.get('par_type', 'str')
            if ((par_type != 'str') and (par_type != 'int') and
                (par_type != 'bool') and (par_type != 'float')):
                raise AdelphosException(AdErrno.EINVALID_SYSCALL_PARAM_TYPE,
                                        f"{par_name}, type {par_type} unknown")
            validator = value.get('validator')
            par = SysCallPar(par_name, required, par_type,
                             default_value, validator)
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

            provider_class_str = provider['class']
            provider_class = misc.import_string(provider_class_str)
            syscalls = SysCallGateway._create_syscalls_list(provider_class, provider)
            self._add_syscalls(context, syscalls)


    def clear_syscalls(self):
        self.contexts = dict()


    def _add_syscalls(self, context, syscalls):
        if self.contexts.get(context) is not None:
            raise Exception(f"Context {context} already existing")
        syscall_map = self._transform_list(syscalls)
        self.contexts[context] = syscall_map


    def get_syscall(self, context, cmd):
        rpcs = self.contexts.get(context)
        if rpcs is None:
            raise AdelphosException(AdErrno.ENOSUCH_SYSCALL,
                                    f"unknonw context to run {context}")
        rpc = rpcs.get(cmd)
        if rpc is None:
            raise AdelphosException(AdErrno.ENOSUCH_SYSCALL, 
                                    f"No such remote call {context}.{cmd}")
        return rpc


    def start_sync(self):
        self.register_syscalls(self.kernel, self.realm)


    def stop_sync(self):
        self.clear_syscalls()

