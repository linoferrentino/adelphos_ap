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


from dataclasses import dataclass
from app.sdc.Dependencies import Dependencies
from abc import ABC, abstractmethod
from app.federation.SocialProvider import SocialProvider
from app.logging import gCon
from app.consts import API_POINT
from app.keys import generate_key
from app.dao.ApActorDto import create_local_actor
from app.dao.ApServerDto import create_ap_server
from cryptography.hazmat.primitives import serialization as crypto_serialization
from app.exc.AdelphosException import AdelphosException
from app.exc.AdelphosException import AdErrno
from io import StringIO
from app.federation.SocialUser import SocialUser
from app.dao.ApActorDto import ApActorDto


@dataclass
class UserMsg:
    content: str
    actor_from: ApActorDto
    myself: ApActorDto


class UserInbox(SocialUser):

    def __init__(self, actor_dto, aListener = None):
        self.actor_dto = actor_dto
        if aListener is None:
            self.messages = []
            self.is_daemon = False
        else:
            self.listener = aListener
            self.is_daemon = True


    async def new_msg(self, actor_from, content):
        msg = UserMsg(content, actor_from, self.actor_dto)
        if self.is_daemon:
            await self.listener.new_post(msg)
        else:
            self.messages.append(msg)


    def count_msg(self):
        return len(self.messages)


    def pop_lst_msg(self):
        (self.messages, msg) = (self.messages[:-1], self.messages[-1])
        return msg

    
class BaseSocial(SocialProvider):

    def __init__(self, vhost):
        super().__init__(vhost)
        self.users = {}


    def is_allowed_rpc_actor(self, user, context, is_query):
        pass


    def create_users(self, users):

        for user in users:
            actor_dto = self.create_if_not_exists(user)

            if user['login_shell'] == False:
                gCon.log(f"skipping non/login user: {user['preferredusername']}")
                continue
            gCon.log(f"[red]create user {user['preferredusername']}[/red]")
            self.users[user['preferredusername']] = \
                    UserInbox(actor_dto)


    def _create_user(self, user):
        
        preferredusername = user['preferredusername']
        gCon.log(f"creating user {user}")

        user_path = API_POINT + f"/users/{preferredusername}"
        user_inbox = user_path + "/inbox"

        private_key =  user.get('private_key')

        if private_key is None:
            private_key = generate_key()
            content = private_key.private_bytes(
                encoding=crypto_serialization.Encoding.PEM,
                format=crypto_serialization.PrivateFormat.PKCS8,
                encryption_algorithm=crypto_serialization.NoEncryption())
        else:
            with open(private_key, "rb") as f:
                content = f.read()
                private_key = crypto_serialization.load_pem_private_key(
                        content, password=None)

        actor = create_local_actor(self.host, user_path, 
                                   user_inbox, preferredusername,
                                content.decode('utf-8'))

        social_dao = self.vhost.get_dep(Dependencies.SOCIAL_DAO)
        social_dao.actor_store(actor)
        assert actor.act.public_key is not None
        #gCon.log(f"this is the actor {actor}")
        return actor


    def add_listener(self, user, listener):
        actor_dto = self.local_actor_get(user)

        if actor_dto is None:
            raise AdelphosException(AdErrno.USER_DOES_NOT_EXIST)
        if user in self.users:
            gCon.log(f"Instance {id(self)} user {user} exists")
            raise AdelphosException(AdErrno.USER_ALREADY_EXISTING)
        gCon.log(f"Instance {id(self)} user {user} does not exist, will add it")
        self.users[user] = UserInbox(actor_dto, listener)


    def remove_listener(self, user):
        actor_dto = self.local_actor_get(user)

        if actor_dto is None:
            raise AdelphosException(AdErrno.USER_DOES_NOT_EXIST)

        if user not in self.users:
            raise AdelphosException(AdErrno.USER_DOES_NOT_EXIST)

        gCon.log(f"instance {id(self)} user {user} delisted")
        del self.users[user]
 

    def login_user(self, user):
        user_stub = self._pri_get_user_stub(user)
        return user_stub


    async def outgoing_message(self, from_user, recipient, message):
        user = self.local_user_get(from_user)
        if user is None:
            raise Exception(f"No user {from_user}")
        social_gw = self.vhost.get_dep(Dependencies.SOCIAL_GATEWAY)
        await social_gw.out_outbox(user.actor_dto, recipient, message)


    async def incoming_message(self, actor_from, recipient, message):
        await recipient.new_msg(actor_from, message)


    def _pri_get_user_stub(self, user):
        user_stub = self.users.get(user)
        if user_stub is None:
            raise AdelphosException(AdErrno.USER_DOES_NOT_EXIST)
        return user_stub

 
    def local_user_get(self, user_name):
        user_local = self.users.get(user_name)
        if user_local is None:
            gCon.log(f"{id(self)} user {user_name} not present")
        return user_local


    def create_if_not_exists(self, user):
        actor_dto = self.social_dao.actor_get(self.host, user['preferredusername'])
        if actor_dto is None:
            actor_dto = self._create_user(user)
        return actor_dto


    def local_actor_get(self, user_name):
        return self.social_dao.actor_get(self.host, user_name)


    def start_sync(self):
        config = self.vhost.conf()
        self.social_dao = self.vhost.get_dep(Dependencies.SOCIAL_DAO)
        soc_cnf  = config.get_social_config()
        host = config.get_host()
        gCon.log(f"{id(self)} This is the conf {soc_cnf} [red]{id(self)}[/red] for host {host}")
        self.host = host

        users = soc_cnf['users']
        self.create_users(users)


    def stop_sync(self):
        pass


    def get_user_tag(self, user):
        pass


    def set_user_tag(self, user, tag):
        pass
