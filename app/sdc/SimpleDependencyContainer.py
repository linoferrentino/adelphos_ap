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
from tests.testers.TestKernel import TestKernel
from tests.testers.SimpleSocialGateway import SimpleSocialGateway
from tests.testers.SimpleSocialDao import SimpleSocialDao
from app.cli.StandardCliProvider import StandardCliProvider
from app.cli.AdelphosCliRouter import AdelphosCliRouter
from app.sdc.Dependencies import Dependencies
from app.federation.BaseSocial import BaseSocial
from app.federation.LifespanAware import LifespanAware
from app.federation.store.SqliteSocialDao import SqliteSocialDao
from app.core.Adelphos import Adelphos
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


class SimpleDependencyContainer(LifespanAware):

    def __init__(self, instance, config):
                 
        self.instance = instance
        self.config_data = config
        self.config = Config(instance, self.config_data)

        self.async_modules = list()
        self.sync_modules = list()
        self.routable_modules = list()

        self._build_modules()

        #self.mods[Dependencies.ROUTER] = AdelphosRouter(self.vhost)
        #self.mods[Dependencies.SOCIAL] = self._make_social()
        #self.mods[Dependencies.CLI_HANDLER] = self._make_cli_handler()
        #self.mods[Dependencies.SOCIAL_NET] = ActivityPubNetwork(self.vhost)
        #self.mods[Dependencies.CLI_NET] = AdelphosCliRouter(self.vhost)
        #self.mods[Dependencies.SOCIAL_DAO] = self._make_social_dao()
        #self.mods[Dependencies.SOCIAL_GATEWAY] = self._make_social_gateway()
        #self.mods[Dependencies.BACKDOOR_NET] = self._make_backdoor_net()
        #self.mods[Dependencies.SOCIAL_API] = self._make_social_api()
        #self.mods[Dependencies.RPC_API] = SysCallGateway(self.vhost, 'rpc_providers')
        #self.mods[Dependencies.INBOX_API] = SysCallGateway(self.vhost,
        #                                                   'inbox_providers')
        #self.mods[Dependencies.CLI_API] = SysCallGateway(self.vhost, 'cli_providers')


    def _create_module(self, module_name, module):
        #module_name = module['name']
        module_builder_str = module['constructor']
        module_builder = misc.import_string(module_builder_str)
        kwargs = module.get('args')
        
        if kwargs is None:
            module = module_builder(self)
        else:
            module = module_builder(self, **kwargs)
        self.mods[module_name] = module

        if (isinstance(module, LifespanAware)):
            #gCon.log(f"Module {module_name} needs ASYNC starting")
            self.async_modules.append(module)
        elif (isinstance(module, SyncLifespanAware)):
            #gCon.log(f"Module {module_name} needs SYNC starting")
            self.sync_modules.append(module)


    def _build_modules(self):
        self.mods = dict()

        for module_name, module in self.config.modules().items():
            #gCon.log(f"Create module {module}")
            self._create_module(module_name, module)


    def conf(self):
        return self.config


    def conf_mod(self, dependency):
        return self.config.conf_mod(dependency)


    #def _make_social_api(self):
    #    social_api_build = self.config.get_social_api_build()
    #    social_api_type = social_api_build['type']
    #    match social_api_type:
    #        case 'simple':
    #            gCon.log(f"creating simple social api")
    #            social_api = SimpleSocialApiProvider(self.vhost)
    #        case 'adelphos':
    #            gCon.log(f"creating adelphos social api")
    #            social_api = AdelphosApiProvider(self.vhost)
    #    return social_api


    #def _make_backdoor_net(self):
    #    if self.config.is_test_instance():
    #        backdoor_net = BackdoorNet(self.vhost)
    #    else:
    #        backdoor_net = NullNet(self.vhost)
    #    return backdoor_net


    #def _make_social_dao(self):
    #    social_dao_cnf = self.config.get_social_dao_build()
    #    social_dao_type = social_dao_cnf['type']
    #    match social_dao_type:
    #        case 'sqlite':
    #            social_dao = SqliteSocialDao(self.vhost)
    #        case 'simple':
    #            social_dao = SimpleSocialDao(self.vhost)
    #        case _:
    #            raise Exception(f"invalid social dao {social_type}")
    #    return social_dao


    #def _make_social_gateway(self):
    #    social_conf = self.config.get_social_gw_config()
    #    social_type = social_conf['type']
    #    match social_type:
    #        case 'simple':
    #            social_gw = SimpleSocialGateway(self.vhost)
    #        case 'activity_pub':
    #            social_gw = ActivityPubGateway(self.vhost)
    #        case _:
    #            raise Exception(f"invalid type {social_type}")
    #    return social_gw


    #def _make_social(self):
    #    social = BaseSocial(self.vhost)
    #    return social


    #def _make_kernel(self):
    #    kernel_type = self.config.config['sdc']['kernel']['type']
    #    match kernel_type:
    #        case 'test_kernel':
    #            kernel = TestKernel(self.vhost)
    #        case 'adelphos':
    #            kernel = Adelphos(self.vhost)
    #        case _:
    #            raise Exception(f"Invalid kernel {kernel_type}")

    #    return kernel
    

    #def _make_cli_handler(self):

    #    cli_handler_type = self.config.config['sdc']['cli_handler']['type']
    #    match cli_handler_type:
    #        case 'standard_cli':
    #            cli_handler = StandardCliProvider(self.vhost)
    #        case 'cli_stub':
    #            cli_handler = CliHandlerStub(self.vhost)
    #        case _:
    #            raise Exception(f"Invalid cli handler {cli_handler_type}")

    #    return cli_handler


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
        #self.mods[Dependencies.CLI_HANDLER].start_sync()
        #self.mods[Dependencies.SOCIAL_DAO].start_sync()
        #self.mods[Dependencies.SOCIAL].start_sync()
        #self.mods[Dependencies.RPC_API].start_sync()
        #self.mods[Dependencies.INBOX_API].start_sync()
        #self.mods[Dependencies.CLI_API].start_sync()
        for module in self.sync_modules:
            module.start_sync()



    def stop_sync(self):
        #self.mods[Dependencies.CLI_API].stop_sync()
        #self.mods[Dependencies.INBOX_API].stop_sync()
        #self.mods[Dependencies.RPC_API].stop_sync()
        #self.mods[Dependencies.SOCIAL].stop_sync()
        #self.mods[Dependencies.SOCIAL_DAO].stop_sync()
        #self.mods[Dependencies.CLI_HANDLER].stop_sync()
        for module in reversed(self.sync_modules):
            module.stop_sync()


    async def start_async(self):

        for module in self.async_modules:
            await module.start_async()

        #await self.mods[Dependencies.SOCIAL_API].start_async()

    
    async def stop_async(self):

        #await self.mods[Dependencies.SOCIAL_API].stop_async()

        for module in reversed(self.async_modules):
            await module.stop_async()




