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


from app.federation.BaseSocialDao import BaseSocialDao
from app.dao.ApServerDto import ApServerDto
from app.dao.ApServerDto import create_ap_server
from dataclasses import asdict
import json


class SimpleSocialDao(BaseSocialDao):

    def __init__(self, vhost):
        super().__init__(vhost)

        self.servers = {}
        self.users = {}


    def start_sync(self):
        pass


    def stop_sync(self):
        pass


    def srv_get_or_create(self, host_name):
        server_dto_dict = self.servers.get(host_name)
        if server_dto_dict is None:
            server_dto = create_ap_server(host_name)
            self.servers[host_name] = json.dumps(asdict(server_dto))
            return server_dto 
        server_dto_ob = json.loads(server_dto_dict)
        return ApServerDto(**server_dto_ob)


    def actor_get(self, server, user_name):
        pass


    def actor_store(self, actor_dto):
        pass


