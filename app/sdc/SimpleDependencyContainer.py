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
from app.cli.AdelphosCliRouter import AdelphosCliRouter
from app.sdc.Dependencies import Dependencies
from app.config import Config



class SimpleDependencyContainer:

    def __init__(self, vhost, *,
            social = None, 
            kernel = None,
            cli_handler= None):

        instance = vhost.instance_name
        config = vhost.config

        self.config = Config(instance, config)
        self.social = social
        self.kernel = kernel
        self.cli_handler = cli_handler
        self.social_net = ActivityPubNetwork(vhost)
        self.cli_net = AdelphosCliRouter(vhost)


    def get_dep(self, dep):

        match dep:
            case Dependencies.SOCIAL:
                return self.social
            case Dependencies.SOCIAL_NET:
                return self.social_net
            case Dependencies.CLI_NET:
                return self.cli_net
            case Dependencies.KERNEL:
                return self.kernel
            case Dependencies.CONFIG:
                return self.config
            case Dependencies.CLI_HANDLER:
                return self.cli_handler
            case _:
                raise Exception(f"Invalid dep {dep}")

