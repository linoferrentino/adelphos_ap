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

from app.federation.ap.ActivityPubNetwork import ActivityPubNetwork
from app.federation.ap.ActivityPubGateway import ActivityPubGateway
from tests.testers.CliHandlerStub import CliHandlerStub
from tests.testers.SimpleSocialGateway import SimpleSocialGateway
from tests.testers.SimpleSocialDao import SimpleSocialDao
from app.cli.StandardCliProvider import StandardCliProvider
from app.cli.AdelphosCliRouter import AdelphosCliRouter
from app.sdc.Dependencies import Dependencies
from app.federation.BaseSocial import BaseSocial
from app.federation.LifespanAware import LifespanAware
from app.federation.store.SqliteSocialDao import SqliteSocialDao
#from app.core.Adelphos import Adelphos
from app.config import Config
from app.federation.BackdoorNet import BackdoorNet
from app.federation.NullNet import NullNet
from app.ad_api.adelphos.AdelphosApiProvider import AdelphosApiProvider
from tests.testers.SimpleSocialApiProvider import SimpleSocialApiProvider
from app.logging import gCon
from app.core.sys.SysCallGateway import SysCallGateway
from app.AdelphosRouter import AdelphosRouter
from app.federation.SyncLifespanAware import SyncLifespanAware
import app.misc.utils as misc

from dataclasses import dataclass


@dataclass
class PriorityModule:

    priority: int
    module: object

    def __lt__(self, other):
        return self.priority < other.priority


class SimpleDependencyContainer(LifespanAware):

    def __init__(self, instance, config):
                 
        self.instance = instance
        self.config_data = config
        self.config = Config(instance, self.config_data)

        self.async_modules = list()
        self.sync_modules = list()
        self.routable_modules = list()

        self._build_modules()


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
            prio_mod = SimpleDependencyContainer.get_priority_mod(module, module_ob)
            self.async_modules.append(prio_mod)

        elif (isinstance(module_ob, SyncLifespanAware)):
            prio_mod = SimpleDependencyContainer.get_priority_mod(module, module_ob)
            self.sync_modules.append(prio_mod)


    @staticmethod
    def get_priority_mod(module, module_ob):
        if module.get('priority') is not None:
            priority = int(module.get('priority'))
        else:
            priority = 0
        prio_mod = PriorityModule(priority, module_ob)
        return prio_mod


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




