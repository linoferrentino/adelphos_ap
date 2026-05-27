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


from app.federation.SocialDao import SocialDao


class SimpleSocialDao(SocialDao):

    def __init__(self, vhost):
        super().__init__(vhost)


    def start_sync(self):
        pass


    def stop_sync(self):
        pass


    def srv_get_or_create(self, host_name):
        pass


    async def actor_get_or_discover(self, server_dto, key_parsed):
        pass
