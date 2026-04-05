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

from app.logging import gCon
from app.dao.ApActorDto import create_ap_actor
from app.consts import API_POINT
from app.ap_api.ActivityPubGateway import ActivityPubBaseGateway
from app.api.AdelphosException import AdelphosException
from app.federation.SocialProvider import SocialProvider
from app.ap_api.ActivityPubApi import ActivityPubApi
from app.core.MasterAdelphosDao import MasterAdelphosDao
import time


# then there is the Mockup user, it listens to events in ActivityPub
class ActivityPubMockupUser:


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


# this ActivityPub object is also a gateway, it gets the POST messages that
# come from the outside and, if they correspond to real users it will post them
# in the users's inbox.
class ActivityPubMockup(ActivityPubBaseGateway, SocialProvider):


    def __init__(self, db):
        #self.app = app
        self.users = {}
        self.current_logged_user = None
        self.ap_api = ActivityPubApi(self)
        self.dao = MasterAdelphosDao(db)


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


    # the base method to get the activity pub user for the instance, by
    # definition it is in the server zero.
    # this method DOES not discover (it is not async)
    def _select_test_user(self, activity_pub_user):
        ap_actor = self.app.dao.ap_actor_dao.get_from_preferred_username(0,
                              activity_pub_user)
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
        ap_actor = self.app.dao.ap_actor_dao.get_from_preferred_username(0, activity_pub_user)
        if (ap_actor is None):
            return None
        return ('actor', activity_pub_user, f"Mockup actor for instance {self.app.instance}")


    def create_test_users(self):

        if (self.app.config.get('demo_users') is None):
            gCon.log("no demo users defined")
            return

        demo_users = self.app.config['demo_users']

        for demo_user in demo_users:
            is_root = demo_user.get('root') == True
            self.create_demo_user(demo_user['name'], demo_user['alias'],
                        demo_user['password'], is_root)


    # SocialProvider interface.
    def create_user(self, username):
        return self.create_app_actor(username)


    def create_demo_user(self, name, alias, password, is_root):
        #gCon.log(f"Creating ap_actor {name} with alias {alias} and password {password}")
        actor_id = self.create_app_actor(name)

        # this is the part which is not relative to activity pub.
        self.app.kernel.alias_uri_create(actor_id, alias, password)
        if is_root:
            self.app.create_root_actor_impl(actor_id)


    # creates an actor which sits in the instance (only useful for testing)
    def create_app_actor(self, actor_name, forced_id = None):
        user_path = API_POINT + f"/users/{actor_name}"
        user_inbox = user_path + "/inbox"
        # the server is hard coded to zero, we are in the app realm
        myself_actor = create_ap_actor(0, user_path, user_inbox,
                                       actor_name, self.app.public_key)
        if (forced_id is not None):
            myself_actor.actor_id = 0
            actor_id = self.app.dao.ap_actor_dao.store_full_no_ts(myself_actor)
        else:
            actor_id = self.app.dao.ap_actor_dao.store(myself_actor)

        #gCon.log(f"Created actor {actor_name} with id {actor_id}")
        return actor_id


