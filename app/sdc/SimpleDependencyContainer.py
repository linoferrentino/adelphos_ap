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




class SimpleDependencyContainer:

    def __init__(self, config, *,
            social = None, 
            kernel = None,
            cli_handler= None):

        self.social = social
        self.kernel = kernel
        self.cli_handler = cli_handler


