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


from app.core.Daemon import Daemon


class ToyDaemon(Daemon):

    def __init__(self, kernel):
        super().__init__(kernel)


    async def start_impl(self):
        pass


    async def stop_impl(self):
        pass



