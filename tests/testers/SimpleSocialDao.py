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
from app.dao.ApServerDto import create_ap_server
from dataclasses import asdict
from app.logging import gCon
from app.sdc.Dependencies import Dependencies
import json


class SimpleSocialDao(BaseSocialDao):

    def __init__(self, kernel):
        super().__init__(kernel)

        self.servers = {}
        self.next_srv_id = 1
        self.next_act_id = 1


    def start_sync(self):
        pass


    def stop_sync(self):
        pass

    
    def actor_get_from_id(self, actor_id):
        assert False


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
            self.servers[host_name] = srv_info
            return server_dto.server_id
        server_dto_ob = json.loads(server_dto_dict['srv'])
        server_dto = ApServerDto(**server_dto_ob)
        gCon.log(f"Create the server {host_name} with id {server_dto.server_id}")
        return server_dto.server_id


    def actor_get_from_parsed_url(self, parsed_url):
        if len(parsed_url.netloc) == 0:
            host = self.conf.get_host()
        else:
            host = parsed_url.netloc

        user_name = parsed_url.path.split('/')[-1]
    
        gCon.log(f"ASKING user {host} ---> {user_name}")
        actor = self._actor_get_host(host, user_name)
        return actor


    def actor_get(self, host_name, user_name):

        return self._actor_get_host(host_name, user_name)


    def _actor_get_host(self, host, user_name):

        srv_info = self.servers.get(host)
        if srv_info is None:
            gCon.log(f"Not found host {host}")
            return None
        users = srv_info['users']
        actor_dto_dict = users.get(user_name)
        if actor_dto_dict is None:
            gCon.log(f"Not found user {user_name}")
            return None
        actor_dto = ApActorDto(**json.loads(actor_dto_dict))
        actor_dto.srv = ApServerDto(**actor_dto.srv)
        actor_dto.act = ApActorImpl(**actor_dto.act)
        return actor_dto


    def _store_actor_impl(self, actor_dto):

        host = self.kernel.config.get_host()

        gCon.log(f"[red]{host}: storing {actor_dto.get_social_handle()}[/red]")

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


        server_inf['users'][actor_dto.act.preferred_username] = \
                json.dumps(asdict(actor_dto))

        gCon.log(f"[red]Stored {actor_dto.act.preferred_username} with id \
{actor_dto.act.actor_id}[/red]")

        return actor_dto.act.actor_id


