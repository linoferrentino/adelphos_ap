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


from app.federation.SocialListener import SocialListener
from app.misc.WrapInt import WrapInt
from app.logging import gCon

from abc import abstractmethod, ABC

class SocialGateway(ABC):

    @abstractmethod
    async def in_inbox(self, user, request):
        pass


class SocialGateway_NO(SocialListener):


    def __init__(self, social, social_tenant):

        self.social = social
        self.social_tenant = social_tenant
        social.create_or_register_user(social_tenant, True, self)
        self.requests = dict()
        self.remote_api_id = WrapInt()


    async def post_and_wait_ans(self, user, message, *, timeout = 10):
        pass


    def api_gw_waitable(self, api_id, user_handle, req_json):
        
        self.social.post_message(user_handle, req_json)

        yield "ooo"




    def api_req_wait(self, user_handle, request_json):

        api_id = 88

        self.requests[api_id] = "xx"

        api = self.api_gw_waitable(api_id, user_handle, request_json)

        val = next(api)
        gCon.log(f"I have obtained {val}")

        return val


    async def new_post(self, post):
        return


    def new_post_sync(self, post):

        api_id = self._get_request_id(post)

        api = self.request.get(api_id)

        next(api)

