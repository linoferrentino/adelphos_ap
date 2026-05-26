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
from tests.testers.fixtures import CliHandlerStub
from tests.testers.TestKernel import TestKernel
from app.cli.StandardCliProvider import StandardCliProvider
from app.cli.AdelphosCliRouter import AdelphosCliRouter
from app.sdc.Dependencies import Dependencies
from app.federation.SimpleSocial import SimpleSocial
from app.config import Config



class SimpleDependencyContainer:

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
        self.gateway = self._make_gateway(vhost)
        self.transport = None


    def _make_social(self):
        social = SimpleSocial(('demo1', 'demo2'), self.vhost)
        return social


    def _make_kernel(self):
        kernel = TestKernel(self.vhost)
        return kernel


    def _make_gateway(self, vhost):
        gateway = None
        return gateway


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
            case _:
                raise Exception(f"Invalid dep {dep}")
        return dep_ob


    def start_sync(self):
        pass


    def stop_sync(self):
        pass

