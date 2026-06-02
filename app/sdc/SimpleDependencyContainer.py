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
#from app.federation.social.SocialStub import SocialStub
#from app.federation.social.ActivityPubSocial import ActivityPubSocial
from app.federation.BaseSocial import BaseSocial
from app.federation.LifespanAware import LifespanAware
from app.federation.store.SqliteSocialDao import SqliteSocialDao
from app.core.Adelphos import Adelphos
from app.config import Config



class SimpleDependencyContainer(LifespanAware):

    def __init__(self, vhost):
                 
        instance = vhost.instance_name
        config = vhost.config

        self.vhost = vhost
        self.config = Config(instance, config)
        self.social = self._make_social()
        self.kernel = self._make_kernel()
        self.cli_handler = self._make_cli_handler()
        self.social_net = ActivityPubNetwork(vhost)
        self.cli_net = AdelphosCliRouter(vhost)
        self.social_dao = self._make_social_dao()
        self.social_gateway = self._make_social_gateway()
        self.transport = None


    def _make_social_dao(self):
        social_dao_cnf = self.config.get_social_dao_build()
        social_dao_type = social_dao_cnf['type']
        match social_dao_type:
            case 'sqlite':
                social_dao = SqliteSocialDao(self.vhost)
            case 'simple':
                social_dao = SimpleSocialDao(self.vhost)
            case _:
                raise Exception(f"invalid social dao {social_type}")
        return social_dao


    def _make_social_gateway(self):
        social_conf = self.config.get_social_gw_config()
        social_type = social_conf['type']
        match social_type:
            case 'simple':
                social_gw = SimpleSocialGateway(self.vhost)
            case 'activity_pub':
                social_gw = ActivityPubGateway(self.vhost)
            case _:
                raise Exception(f"invalid type {social_type}")
        return social_gw


    def _make_social(self):
        #social_type = self.config.get_social_type()
        #match social_type:
        #    case 'simple':
        #        social = SocialStub(self.vhost)
        #    case 'activity_pub':
        #        social = ActivityPubSocial(self.vhost)
        #return social
        social = BaseSocial(self.vhost)
        return social


    def _make_kernel(self):
        kernel_type = self.config.config['sdc']['kernel']['type']
        match kernel_type:
            case 'test_kernel':
                kernel = TestKernel(self.vhost)
            case 'adelphos':
                kernel = Adelphos(self.vhost)
            case _:
                raise Exception(f"Invalid kernel {kernel_type}")

        return kernel
    

    def _make_cli_handler(self):

        cli_handler_type = self.config.config['sdc']['cli_handler']['type']
        match cli_handler_type:
            case 'standard_cli':
                cli_handler = StandardCliProvider(self.vhost)
            case 'cli_stub':
                cli_handler = CliHandlerStub(self.vhost)
            case _:
                raise Exception(f"Invalid cli handler {cli_handler_type}")

        return cli_handler


    def set_dep(self, dep_type, dep):
        match dep_type:
            case Dependencies.TRANSPORT:
                self.transport = dep
            case _:
                raise Exception(f"Cannot set the dep {dep_type}")


    def get_dep(self, dep):
        match dep:
            case Dependencies.SOCIAL:
                dep_ob = self.social
            case Dependencies.SOCIAL_NET:
                dep_ob = self.social_net
            case Dependencies.CLI_NET:
                dep_ob = self.cli_net
            case Dependencies.KERNEL:
                dep_ob = self.kernel
            case Dependencies.CONFIG:
                dep_ob = self.config
            case Dependencies.CLI_HANDLER:
                dep_ob = self.cli_handler
            case Dependencies.TRANSPORT:
                dep_ob = self.transport
            case Dependencies.SOCIAL_GATEWAY:
                dep_ob = self.social_gateway
            case Dependencies.SOCIAL_DAO:
                dep_ob = self.social_dao
            case _:
                raise Exception(f"Invalid dep {dep}")
        return dep_ob


    def start_sync(self):
        self.cli_handler.start_sync()
        self.social_dao.start_sync()
        self.social.start_sync()


    def stop_sync(self):
        self.social.stop_sync()
        self.social_dao.stop_sync()
        self.cli_handler.stop_sync()


    async def start_async(self):
        await self.kernel.start_async()

    
    async def stop_async(self):
        await self.kernel.stop_async()



