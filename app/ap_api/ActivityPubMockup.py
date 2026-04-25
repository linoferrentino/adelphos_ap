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
#
# this is the Mockup used to store the fake users in this Adelphos instance
# (useful for testing and integrating)

import time
import re
import json
from dataclasses import dataclass

from app.dao.AdelphosDb import AdelphosDb
from fastapi import APIRouter, FastAPI, WebSocket
from fastapi import Request, Depends, Query, HTTPException, status, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from app.ap_api.ActivityPubApi import ActivityPubApi
from app.ap_api.ActivityPubGateway import ActivityPubBaseGateway
from app.ap_api.ActivityPubGateway import ActivityPubGateway
#from app.ap_api.ActivityPubServerModel import ActivityPubServerModel
#from app.ap_api.ActivityPubUserModel import ActivityPubUserModel
from app.api.AdelphosException import AdelphosException
from app.consts import API_POINT
from app.consts import GENERAL_SECTION, PRIVATE_KEY_FILE_KEY
from app.core.MasterAdelphosDao import MasterAdelphosDao
from app.dao.ApActorDto import create_ap_actor
from app.dao.ApServerDto import create_ap_server
from app.federation.SocialListener import SocialListener
from app.federation.SocialProvider import SocialProvider
from app.keys import load_keys
from app.logging import gCon
from app.transport.SyncRouter import SyncRouter
from app.dao.ApServerDao import ApServerDao
from app.dao.ApActorDao import ApActorDao
from app.transport.RouterProvider import RouterProvider
from app.transport.AbstractTransport import AbstractTransport



# then there is the Mockup user, it listens to events in ActivityPub
# usually this models a user which gets notifications by adelphos daemon
class ActivityPubMockupUser(SocialListener):


    def __init__(self, app, server_dto, actor_dto):
        self.app = app
        self.server_dto = server_dto
        self.actor_dto = actor_dto
        # the messages are a simple list, the user then will read them when
        # he logins.
        self.messages = list()


    async def post_message(self, recipient, message):
        await self.app.ap_api.post_to_fediverse_actor(
                self.actor_dto.preferred_username, recipient, message)

    def clear_messages():
        pass


    # how_many will get the last n messages, -1 means all
    def last_n_messages(self, how_many = -1):
        #gCon.log(f"returning {how_many} messages")
        if how_many == -1:
            return self.messages
        return self.messages[-1 * how_many:]


    def incoming_message(self, message):
        self.messages.append(message)


# this is a very simple router to render a FASTApi application an ActivityPub Server
class ActivityPubRouter(APIRouter):


    def __init__(self, apsrv):
        super().__init__()

        @self.get("/.well-known/webfinger",
        description="Adelphos's end point",
        )
        async def webfinger(resource: str = Query(..., alias="resource")):
            return apsrv.webfinger(resource)

    
        @self.get('/users/{username}')
        async def info_user(username : str):
            return apsrv.info_user(username)


        @self.post('/users/{username}/inbox')
        async def user_inbox(username: str, request: Request):
            return await apsrv.user_inbox(username, request)


        # the last route is added only in case of test instance.
        flag = apsrv.do_srv
        del apsrv.do_srv
        if flag == False:
            return


        @self.post('/_backdoor_api_/{cmd}')
        async def _backdoor_api(cmd: str, request : Request):
            body = await request.body()
            body_str = body.decode()
            body_ob = json.loads(body_str)
            res = await apsrv.proc_cmd(cmd, body_ob)
            return { 'res' : res }



class ActivityPubSyncRouter(SyncRouter):
    

    def __init__(self, ap_mockup):
        super().__init__()
        # the sync interface is used to bypass the message dispatching.
        super()._register_post_route('/user/(.*)/inbox', ap_mockup.user_inbox_sync)



@dataclass
class ActivityPubMockupConfig:
    transport : AbstractTransport
    host : str
    db_name : str = ":memory:"
    key_file_name : str = ":memory:"
    do_srv : bool = False


# this ActivityPub object is also a gateway, it gets the POST messages that
# come from the outside and, if they correspond to real users it will post them
# in the users's inbox.
class ActivityPubMockup(ActivityPubBaseGateway, SocialProvider, RouterProvider):


    def __init__(self, config):
        #self.app = app

        #db_name = config['General']['db_name']
        db = AdelphosDb(':memory:')

        self.transport = config.transport
        self.users = {}
        self.current_logged_user = None
        self.ap_api = ActivityPubApi(self)
        #self.dao = MasterAdelphosDao(db)
        #self.ap_srv_model = ActivityPubServerModel(db)
        #self.ap_user_model = ActivityPubUserModel(db)

        self.ap_actor_dao = ApActorDao(db)
        self.ap_server_dao = ApServerDao(db)

        self.ap_gateway = ActivityPubGateway(self)
        self.do_srv = config.do_srv

        key_file = config.key_file_name
        (pub_key, priv_key) = load_keys(key_file)
        self.public_key = pub_key
        self.private_key = priv_key


    def initialization(self):

        host = self.config['General']['host']
        #self.srv_id = self.ap_srv_model.new_server(host)
        self.local_server = self.ap_server_dao.create_from_hostname(host)


    def load_fixture(self):
        host = self.config['General']['host']
        self.srv_id = self.ap_srv_model.get_from_host_name(host)


    async def user_inbox(username: str, request: Request):

        #gCon.log(f"[red]post inbox {username}[/red]")

        res_code = 404
        if username == DAEMON_ID:

            # this will return the return code and will process the request asynchronously
            res_code = await self.ap_gateway.new_request(request)

        elif test_instance:

            # the message is not for the daemon, it might be for some test users
            # that I have .
            res_code = await self.new_request(request)
            
        return Response(status_code = res_code)


    def info_user_kw(self, params):
        return self.info_user(params['username'])


    def info_user(self, username):

        user_info = self.ap_user_info(username)

        if (user_info is None):
            return Response(status_code=404)

        host = self.config['General']['host']
        host_api = host + API_POINT

        response_ob = {
            "@context": [
                "https://www.w3.org/ns/activitystreams",
                "https://w3id.org/security/v1",
            ],
            "id": f"https://{host_api}/users/{username}",
            "inbox": f"https://{host_api}/users/{username}/inbox",
            "outbox": f"https://{host_api}/users/{username}/outbox",
            "type": user_info[0],
            "name": user_info[2],
            "preferredUsername": user_info[1],
            "publicKey": {
                "id": f"https://{host_api}/users/{username}#main-key",
                "owner": f"https://{host_api}/users/{username}",
                "publicKeyPem": self.public_key
            }
        }

        resp_json = jsonable_encoder(response_ob)
        response = JSONResponse(content = resp_json)
        response.headers['Content-Type'] = 'application/activity+json'
        return response


    def webfinger_kw(self, kw):
        return self.webfinger(kw['resource'])


    def webfinger(self, resource):

        host = self.config['General']['host']
        host_api = host + API_POINT

        ap_user_match = re.match('acct:(.*?)@(.*)$', resource)
        if (ap_user_match is None):
            return Response(status_code=401)

        host_rex = ap_user_match.group(2)
        if (host_rex != host):
            return Response(status_code=404)

        ap_user_rex = ap_user_match.group(1)
        if (self.ap_user_exists(ap_user_rex) == False):
            return Response(status_code=404)

        response = Response(
            content=json.dumps({
                "subject": resource,
                "links": [
                    {
                        "rel": "self",
                        "type": "application/activity+json",
                        "href": f"https://{host_api}/users/{ap_user_rex}"
                    }
                ]
            })
        )
        
        response.headers['Content-Type'] = 'application/jrd+json'
        return response




    # this is the router relative to the activity pub interface.
    def get_async_router(self):

        ap_router = ActivityPubRouter(self)
        return ap_router


    def register_sync_routes(self, router):
        router._register_get_route("/.well-known/webfinger", self.webfinger_kw, "resource")
        router._register_get_route(API_POINT + "/users/(?P<username>.*)", 
                                   self.info_user_kw, "username")


    def ensure_logged_user(func):

        async def force_login(self, body_ob):
           if self.current_logged_user is None:
               raise AdelphosException('no logged user')
           return await func(self, body_ob)

        return force_login


    async def proc_cmd(self, cmd, body_ob):

        match cmd:
            case 'login':
                user = body_ob['user']
                self.force_login(user)
            case 'post':
                await self.post_message(body_ob)
            case 'get_unread_messages':
                # in this case I might return a list.
                return await self.unread_messages(body_ob)
            case _:
                raise AdelphosException(f"invalid test command {cmd}")

        # if I am here, all is good, but the answer is only a number.
        return 0


    @ensure_logged_user
    async def post_message(self, body_ob):
        recipient = body_ob['recipient']
        msg = body_ob['msg']
        await self.current_logged_user.post_message(recipient, msg)


    @ensure_logged_user
    async def unread_messages(self, body_ob):
        how_many = body_ob['how_many']
        return self.current_logged_user.last_n_messages(how_many)


    # the base method to get the activity pub user for the instance.
    # this method DOES not discover (it is not async)
    def _select_test_user(self, activity_pub_user):
        ap_actor = self.ap_actor_dao.get_from_preferred_username(
                self.local_server.server_id, activity_pub_user)
        #gCon.log(f"Obtained actor {ap_actor} for {activity_pub_user}")
        return ap_actor


    # queries the db in order to get the answer
    def ap_user_exists(self, activity_pub_user):
        # OK, I have to query the db, the server MUST be zero, I only
        # accept activities for local users.
        ap_actor = self._select_test_user(activity_pub_user)
        if (ap_actor is None):
            return False
        return True


    # this method will select a user's inbox to deliver a post message.
    # it is called when we receive a mention for another user.
    def select_user_inbox(self, activity_pub_user):
        self.force_login(activity_pub_user)


    # override from Gateway
    async def proc_request(self, req_str):
        #gCon.log(f"msg {req_str} for {self.current_logged_user}")
        self.current_logged_user.incoming_message(req_str)


    # called in testing to allow the possibility to login
    # and send real activity pub posts
    def force_login(self, activity_pub_user):
        # there is already a user.
        if (user_handle := self.users.get(activity_pub_user)) is not None:
            return
        # the condition is on the actor.
        ap_actor = self._select_test_user(activity_pub_user)
        if ap_actor is None:
            raise AdelphosException(f"Unknown user {activity_pub_user}")
        ap_server = self.app.dao.ap_server_dao.get_from_id(0)
        #gCon.log(f"forced login of {ap_actor} on {ap_server}")
        ap_user = ActivityPubMockupUser(self.app, ap_server, ap_actor)
        self.users[activity_pub_user] = ap_user
        self.current_logged_user = ap_user


    def ap_user_info(self, activity_pub_user):
        ap_actor = self.ap_actor_dao.get_from_preferred_username(
                self.local_server.server_id, activity_pub_user)
        if (ap_actor is None):
            return None
        instance = self.config['General']['name']
        return ('actor', activity_pub_user, f"Mockup actor for instance {instance}")


    #def create_test_users_OLD(self):

    #    if (self.app.config.get('demo_users') is None):
    #        gCon.log("no demo users defined")
    #        return

    #    demo_users = self.app.config['demo_users']

    #    for demo_user in demo_users:
    #        is_root = demo_user.get('root') == True
    #        self.create_demo_user(demo_user['name'], demo_user['alias'],
    #                    demo_user['password'], is_root)


    # SocialProvider interface.
    def create_user(self, username, is_daemon):
        return self.create_app_actor(username, is_daemon)


    def discover_user(self, username, maybe = False):
        (srv_ob, actor_ob) = self.ap_api.get_or_discover_actor(username, maybe)
        return actor_ob.actor_id


    def create_internal_user(self, username):
        return self.create_app_actor(username, False)


    #def create_demo_user(self, name, alias, password, is_root):
    #    #gCon.log(f"Creating ap_actor {name} with alias {alias} and password {password}")
    #    actor_id = self.create_app_actor(name)

    #    # this is the part which is not relative to activity pub.
    #    self.app.kernel.alias_uri_create(actor_id, alias, password)
    #    if is_root:
    #        self.app.create_root_actor_impl(actor_id)


    # creates an actor which sits in the instance (only useful for testing)
    def create_app_actor(self, actor_name, is_daemon = True):
        user_path = API_POINT + f"/users/{actor_name}"
        user_inbox = user_path + "/inbox"

        # the server is hard coded to zero, we are in the app realm
        myself_actor = create_ap_actor(self.local_server.server_id, user_path, user_inbox,
                                       actor_name, self.public_key)
        #if (forced_id is not None):
        #    myself_actor.actor_id = 0
        #    actor_id = self.app.dao.ap_actor_dao.store_full_no_ts(myself_actor)
        #else:
        actor_id = self.ap_actor_dao.store(myself_actor)

        #actor_id = self.ap_user_model.new_user(self.srv_id,
        #        user_path, user_inbox, actor_name, self.public_key, is_daemon)

        #gCon.log(f"Created actor {actor_name} with id {actor_id}")
        return actor_id


