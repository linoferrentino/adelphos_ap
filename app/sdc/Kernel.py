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


from dataclasses import dataclass

from app.config import Config
from app.federation.LifespanAware import LifespanAware
from app.federation.SyncLifespanAware import SyncLifespanAware
from app.logging import gCon
from app.sdc.Dependencies import Dependencies

import app.misc.utils as misc


@dataclass
class PriorityOb:

    priority: int
    ob: object

    def __lt__(self, other):
        return self.priority < other.priority


class Kernel(LifespanAware):

    def __init__(self, instance, config):
                 
        self.instance = instance
        self.config_data = config
        self.config = Config(instance, self.config_data)

        self.async_modules = list()
        self.sync_modules = list()
        self.routable_modules = list()
        self.daemons = list()

        self.daemons_dict = dict()
        self.mods = dict()

        self._build_modules()
        self._build_daemons()


    def _create_dyn_object(self, module):
        module_builder_str = module['constructor']
        module_builder = misc.import_string(module_builder_str)
        kwargs = module.get('args')
        
        if kwargs is None:
            module_ob = module_builder(self)
        else:
            module_ob = module_builder(self, **kwargs)

        prio_mod = Kernel._get_priority_mod(module, module_ob)
        return prio_mod


    def _create_daemon(self, daemon_name, daemon):
        prio_mod = self._create_dyn_object(daemon)
        self.daemons.append(prio_mod)
        self.daemons_dict[daemon_name] = prio_mod.ob


    def _create_module(self, module_name, module):

        prio_mod = self._create_dyn_object(module)

        self.mods[module_name] = prio_mod.ob

        if (isinstance(prio_mod.ob, LifespanAware)):
            self.async_modules.append(prio_mod)

        elif (isinstance(prio_mod.ob, SyncLifespanAware)):
            self.sync_modules.append(prio_mod)


    @staticmethod
    def _get_priority_mod(module, module_ob):
        if module.get('priority') is not None:
            priority = int(module.get('priority'))
        else:
            priority = 0
        prio_mod = PriorityOb(priority, module_ob)
        return prio_mod


    def _build_daemons(self):
        daemons = self.config.daemons_maybe()
        if (daemons is None):
            return

        for daemon_name, daemon in daemons.items():
            self._create_daemon(daemon_name, daemon)

        self.daemons.sort()


    def _build_modules(self):

        for module_name, module in self.config.modules().items():
            self._create_module(module_name, module)

        self.async_modules.sort()
        self.sync_modules.sort()


    def conf(self):
        return self.config


    def conf_mod(self, dependency):
        return self.config.conf_mod(dependency)


    def set_dep(self, dep_type, dep):
        match dep_type:
            case Dependencies.TRANSPORT:
                self.mods[Dependencies.TRANSPORT] = dep
            case _:
                raise Exception(f"Cannot set the dep {dep_type}")


    def get_dep(self, dep):
        dep_mod = self.mods.get(dep)
        return dep_mod


    def get_daemon(self, daemon):
        return self.daemons_dict.get(daemon)


    def start_sync(self):
        for module in self.sync_modules:
            module.ob.start_sync()


    def stop_sync(self):
        for module in reversed(self.sync_modules):
            module.ob.stop_sync()


    async def start_async(self):
        for module in self.async_modules:
            await module.ob.start_async()
        await self.start_daemons()


    async def start_daemons(self):
        for daemon in self.daemons:
            await daemon.ob.start()


    async def stop_daemons(self):
        for daemon in reversed(self.daemons):
            await daemon.ob.stop()

    
    async def stop_async(self):
        await self.stop_daemons()
        for module in reversed(self.async_modules):
            gCon.log(f"stopping module {module}")
            await module.ob.stop_async()




