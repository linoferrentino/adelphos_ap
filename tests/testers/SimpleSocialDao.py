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
from app.dao.ApActorDto import ApActorDto
from app.dao.ApServerDto import create_ap_server
from dataclasses import asdict
from app.logging import gCon
import json


class SimpleSocialDao(BaseSocialDao):

    def __init__(self, vhost):
        super().__init__(vhost)

        self.servers = {}
        self.next_srv_id = 1


    def start_sync(self):
        pass


    def stop_sync(self):
        pass


    def srv_get_or_create(self, host_name):
        server_dto_dict = self.servers.get(host_name)
        if server_dto_dict is None:
            server_dto = create_ap_server(host_name)
            server_dto.server_id = self.next_srv_id
            self.next_srv_id += 1
            srv_info = {
                    'srv' : json.dumps(asdict(server_dto)),
                    'users' : {},
                    }
            gCon.log(f"this is server info {srv_info}")
            self.servers[host_name] = srv_info
            return server_dto 
        server_dto_ob = json.loads(server_dto_dict['srv'])
        return ApServerDto(**server_dto_ob)


    def actor_get_from_parsed_url(self, parsed_url):
        raise NotImplemented("TODO")


    def actor_get(self, server, user_name):

        srv_info = self.servers.get(server.host_name)
        if srv_info is None:
            return None
        users = srv_info['users']
        actor_dto_dict = users.get(user_name)
        if actor_dto_dict is None:
            return None
        actor_dto = ApActorDto(**json.loads(actor_dto_dict))
        gCon.log("FOUND THE ACTOR!")
        return actor_dto


    def actor_store(self, actor_dto):

        found = False
        #gCon.log(f"storing actor {actor_dto}")
        for k, server_inf in self.servers.items():
            #gCon.log(f"searching info {server_inf}")
            srv_dto_dict = json.loads(server_inf['srv'])
            server_dto = ApServerDto(**srv_dto_dict)
            if server_dto.server_id  == actor_dto.server_fk:
                found = True
                break

        if found == False:
            raise Exception(f"foreign key failed {actor_dto}")

        server_inf['users'][actor_dto.preferred_username] = \
                json.dumps(asdict(actor_dto))




