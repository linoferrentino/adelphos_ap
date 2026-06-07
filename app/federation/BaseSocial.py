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


from app.sdc.Dependencies import Dependencies
from abc import ABC, abstractmethod
from app.federation.SocialProvider import SocialProvider
from app.logging import gCon
from app.consts import API_POINT
from app.keys import generate_key
from app.dao.ApActorDto import create_ap_actor
from cryptography.hazmat.primitives import serialization as crypto_serialization
from app.exc.AdelphosException import AdelphosException
from app.exc.AdelphosException import AdErrno
from io import StringIO
from app.federation.SocialUser import SocialUser


class UserStub(SocialUser):

    def __init__(self, actor_dto, aListener = None):
        self.actor_dto = actor_dto
        if aListener is None:
            self.messages = []
            self.is_daemon = False
        else:
            self.listener = aListener
            self.is_daemon = True


    async def new_msg(self, actor_from, msg):
        if self.is_daemon:
            await self.listener.new_post(actor_from, msg)
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


    def create_users(self, server, users):

        for user in users:
            actor_dto = self.create_if_not_exists(user)

            if user['login_shell'] == False:
                gCon.log(f"skipping non/login user: {user['preferredusername']}")
                continue
            self.users[user['preferredusername']] = \
                    UserStub(actor_dto)


    def _create_user(self, server, user):
        
        preferredusername = user['preferredusername']
        #gCon.log(f"creating user {user}")

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
                #gCon.log(f"private key {content}")
                private_key = crypto_serialization.load_pem_private_key(
                        content, password=None)

        public_key = BaseSocial._get_public_key(private_key)
        #gCon.log(f"private key {content}")

        actor = create_ap_actor(server.server_id,
                         user_path, user_inbox, preferredusername,
                                content.decode('utf-8'), public_key)

        social_dao = self.vhost.get_dep(Dependencies.SOCIAL_DAO)
        social_dao.actor_store(actor)
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
        self.users[user] = UserStub(actor_dto, listener)


    #def create_or_register_user_XX(self, user, *, listener = None):
    #    if user in self.users:
    #        raise AdelphosException(AdErrno.USER_ALREADY_EXISTING)
    #    self.users[user] = UserStub(user, listener)


    def login_user(self, user):
        user_stub = self._pri_get_user_stub(user)
        return user_stub


    async def outgoing_message(self, user, message):
        transport = self.vhost.get_dep(Dependencies.TRANSPORT)
        await transport.post_json(user, {
            'msg' : message
            })


    async def incoming_message(self, actor_from, recipient, message):
        #user_stub = self._pri_get_user_stub(user)
        #sender_id = 999
        await recipient.new_msg(actor_from, message)


    def _pri_get_user_stub(self, user):
        user_stub = self.users.get(user)
        if user_stub is None:
            raise AdelphosException(AdErrno.USER_DOES_NOT_EXIST)
        return user_stub

 
    #def local_user_exists(self, user: str) -> bool:
    def local_user_get(self, user_name):
        user_local = self.users.get(user_name)
        return user_local


    def create_if_not_exists(self, user):
        actor_dto = self.social_dao.actor_get(self.server_dto, 
                                              user['preferredusername'])
        if actor_dto is None:
            actor_dto = self._create_user(self.server_dto, user)
        return actor_dto


    @staticmethod
    def _get_public_key(private_key):
        public_key = private_key.public_key().public_bytes(
                encoding=crypto_serialization.Encoding.PEM,
                format=crypto_serialization.PublicFormat.SubjectPublicKeyInfo)\
                        .decode('utf-8')
        return public_key


    def local_actor_get(self, user_name):
        actor_dto = self.social_dao.actor_get(self.server_dto, user_name)

        if actor_dto is None:
            return None

        private_key = crypto_serialization.load_pem_private_key(
                actor_dto.key.encode('utf-8'), password=None)
        public_key = BaseSocial._get_public_key(private_key)
        actor_dto.public_key = public_key
        #gCon.log(f"PUBLIC KEY {public_key}")
        return actor_dto


    def start_sync(self):
        config = self.vhost.get_dep(Dependencies.CONFIG)
        self.social_dao = self.vhost.get_dep(Dependencies.SOCIAL_DAO)
        soc_cnf  = config.get_social_config()
        host = config.get_host()
        gCon.log(f"This is the conf {soc_cnf} for host {host}")

        self.server_dto = self.social_dao.srv_get_or_create(host)
        gCon.log(f"This is the host {self.server_dto}")

        users = soc_cnf['users']
        self.create_users(self.server_dto, users)


    def stop_sync(self):
        pass
