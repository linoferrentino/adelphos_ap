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
from app.federation.SocialProvider import SocialProvider
from app.exc.AdelphosException import AdelphosException
from app.exc.AdelphosException import AdErrno
from app.logging import gCon


class UserStub:

    def __init__(self, user, aListener = None):
        self.user = user
        if aListener is None:
            self.messages = []
            self.is_daemon = False
        else:
            self.listener = aListener
            self.is_daemon = True


    async def new_msg(self, sender_id, msg):
        if self.is_daemon:
            await self.listener.new_post(sender_id, msg)
        else:
            self.messages.append(msg)

    def count_msg(self):
        return len(self.messages)


    def pop_lst_msg(self):
        (self.messages, msg) = (self.messages[:-1], self.messages[-1])
        return msg


class SimpleSocial(SocialProvider):

    #def __init__(self, user_list, vhost):
    def __init__(self, vhost):
        super().__init__(vhost)
        #self.users = { user: UserStub(user) for user in user_list }


    def local_user_exists(self, user: str) -> bool:
        user_local = self.users.get(user)
        if user_local is None:
            return False
        return True

    
    def _pri_get_user_stub(self, user):
        user_stub = self.users.get(user)
        if user_stub is None:
            raise AdelphosException(AdErrno.USER_DOES_NOT_EXIST)
        return user_stub
 

    async def incoming_message(self, user, message):
        user_stub = self._pri_get_user_stub(user)
        msg = message['msg']
        sender_id = 999
        await user_stub.new_msg(sender_id, msg)


    async def outgoing_message(self, user, message):
        transport = self.vhost.get_dep(Dependencies.TRANSPORT)
        await transport.post_json(user, {
            'msg' : message
            })


    def login_user(self, user):
        user_stub = self._pri_get_user_stub(user)
        return user_stub


    def create_or_register_user(self, user, *, listener = None):
        if user in self.users:
            raise AdelphosException(AdErrno.USER_ALREADY_EXISTING)
        self.users[user] = UserStub(user, listener)


    async def start_async(self):
        config = self.vhost.get_dep(Dependencies.CONFIG)
        demo_users = config.get_social_config()['demo_users']
        self.users = { user: UserStub(user) for user in demo_users}


    async def stop_async(self):
        pass



