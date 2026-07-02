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
from app.dao.ApActorDto import ApActorImpl
#from app.dao.ApActorDto import ApActorPack
from app.dao.ApServerDto import create_ap_server
from dataclasses import asdict
from app.logging import gCon
from app.sdc.Dependencies import Dependencies
import json


class SimpleSocialDao(BaseSocialDao):

    def __init__(self, vhost):
        super().__init__(vhost)

        self.servers = {}
        self.next_srv_id = 1
        self.next_act_id = 1


    def start_sync(self):
        pass


    def stop_sync(self):
        pass


    def _srv_get_or_create(self, host_name):
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
            return server_dto.server_id
        server_dto_ob = json.loads(server_dto_dict['srv'])
        server_dto = ApServerDto(**server_dto_ob)
        return server_dto.server_id


    def actor_get_from_parsed_url(self, parsed_url):
        if len(parsed_url.netloc) == 0:
            host = self.vhost.conf().get_host()
        else:
            host = parsed_url.netloc
    
        gCon.log(f"Searching actor @{parsed_url.path}@{host}")
        actor = self._actor_get_host(host, parsed_url.path)
        return actor


    def actor_get(self, host_name, user_name):

        return self._actor_get_host(host_name, user_name)


    def _actor_get_host(self, host, user_name):
        #gCon.log(f"searching {host} and user {user_name}")

        srv_info = self.servers.get(host)
        if srv_info is None:
            #gCon.log("Not found the host")
            return None
        users = srv_info['users']
        #gCon.log(f"The users for host {host} are {users}")
        actor_dto_dict = users.get(user_name)
        if actor_dto_dict is None:
            #gCon.log("Not found the actor")
            return None
        actor_dto = ApActorDto(**json.loads(actor_dto_dict))
        gCon.log(f"server {actor_dto.srv}")
        actor_dto.srv = ApServerDto(**actor_dto.srv)
        actor_dto.act = ApActorImpl(**actor_dto.act)
        gCon.log(f"FOUND THE ACTOR! {user_name}")
        return actor_dto


    def _store_actor_impl(self, actor_dto):

        #BaseSocialDao._fill_public_key(actor_dto)
        #gCon.log(f"store {actor_dto}")

        found = False
        for k, server_inf in self.servers.items():
            srv_dto_dict = json.loads(server_inf['srv'])
            server_dto = ApServerDto(**srv_dto_dict)
            if server_dto.server_id  == actor_dto.act.server_fk:
                found = True
                break

        if found == False:
            raise Exception(f"foreign key failed {actor_dto}")

        actor_dto.act.actor_id = self.next_act_id
        self.next_act_id += 1

        #gCon.log(f"Now the server inf is {server_inf}")

        server_inf['users'][actor_dto.act.preferred_username] = \
                json.dumps(asdict(actor_dto))

        return actor_dto.act.actor_id


