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

from app.federation.SocialListener import SocialListener

class SocialGateway(SocialListener):


    def __init__(self, social, social_tenant):

        self.social = social
        self.social_tenant = social_tenant
        social.create_or_register_user(social_tenant, True, self)
        self.requests = dict()


    def api_gw_waitable(self, api_id):
        
        self.social.post_message(f"@{DBSOCIAL_NAME}@rctx.uri_ob.host",
                                 f"giveme {rctx.uri_str} {api_id}")

        yield



    def api_req_wait(self, user_handle, request_json):

        api_id = 88

        self.requests[api_id] = "xx"

        api = self.api_gw_waitable()

        next(api)


    async def new_post(self, post):
        return


    def new_post_sync(self, post):

        api_id = self._get_request_id(post)

        api = self.request.get(api_id)

        next(api)

