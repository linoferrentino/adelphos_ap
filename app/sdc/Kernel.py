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
class PriorityModule:

    priority: int
    module: object

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

        self._build_modules()
        self._build_daemons()


    def _create_module(self, module_name, module):
        module_builder_str = module['constructor']
        module_builder = misc.import_string(module_builder_str)
        kwargs = module.get('args')
        
        if kwargs is None:
            module_ob = module_builder(self)
        else:
            module_ob = module_builder(self, **kwargs)
        self.mods[module_name] = module_ob

        if (isinstance(module_ob, LifespanAware)):
            prio_mod = Kernel.get_priority_mod(module, module_ob)
            self.async_modules.append(prio_mod)

        elif (isinstance(module_ob, SyncLifespanAware)):
            prio_mod = Kernel.get_priority_mod(module, module_ob)
            self.sync_modules.append(prio_mod)


    @staticmethod
    def get_priority_mod(module, module_ob):
        if module.get('priority') is not None:
            priority = int(module.get('priority'))
        else:
            priority = 0
        prio_mod = PriorityModule(priority, module_ob)
        return prio_mod


    def _build_daemons(self):
        daemons = self.config.daemons_maybe()
        if (daemons is None):
            return

        for daemon_name, daemon in daemons.items():
            gCon.log(f"create module name {daemon_name}")


    def _build_modules(self):
        self.mods = dict()

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


    def start_sync(self):
        for module in self.sync_modules:
            module.module.start_sync()


    def stop_sync(self):
        for module in reversed(self.sync_modules):
            module.module.stop_sync()


    async def start_async(self):
        for module in self.async_modules:
            await module.module.start_async()

    
    async def stop_async(self):
        for module in reversed(self.async_modules):
            await module.module.stop_async()




