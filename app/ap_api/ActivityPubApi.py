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

# This is the module which gives services to interact with the Fediverse
# and give to Adelphos the translation to its objects.
from app.api.AdelphosException import AdelphosException
from app.logging import gCon
from app.ap_api.AsyncRequest import AsyncGetReq
import json

class ActivityPubApi:


    # Here I initialize myself with the application, the application is then
    # used to access the specialized DAOs.
    def __init__(self, app):
        self.app = app

    # the api has its own never ending loop to accept the post message that
    # go elsewhere and it has the logic to send and receive messages to
    # other adelphoi instances


    # the close might be not needed, in any case I could store messages which
    # have not been submitted, yet.
    def close(self):
        pass


    # this function will fetch the Fediverse in order to translate a string like
    # @user@host (the classic way to identify a user in Fediverse) into a
    # ApActorDto object.
    # the function will store locally the result, so other queries will fetch
    # the local data.
    async def get_or_discover_actor(self, fediverse_actor_str):

        # I assume the string is well formed, otherwise it won't have an answer
        # it must begin with a @
        (first_char, actor_instance) = (fediverse_actor_str[0], fediverse_actor_str[1:])

        if (first_char != '@'):
            raise AdelphosException(f"Illegal actor identifier {fediverse_actor_str}")

        # now we divide from instance from user name
        user_host = actor_instance.split('@')
        if (len(user_host) != 2):
            raise AdelphosException(f"I was expecting one and only one @ in {actor_instance}")
        (preferred_username, rem_instance) = user_host

        actor_query = f"https://{rem_instance}/.well-known/webfinger?\
resource=acct:{actor_instance}"

        actor_res = AsyncGetReq(actor_query)
        await self.app.async_req_wait(actor_res)

        if (actor_res.status_code != 200):
            raise AdelphosException(
                    f"remote instance {rem_instance} complains!")

        actor_ob = json.loads(actor_res.text)

        subject = actor_ob['subject']
        if ( subject != f"acct:{actor_instance}"):
            raise AdelphosException(f"got {subject} instead!")

        # OK, now we make another query to get his data.
        actor_uri = actor_ob['links'][0]['href']

        ap_actor_res = AsyncGetReq(actor_uri)
        await self.app.async_req_wait(ap_actor_res)
 
        if (ap_actor_res.status_code != 200):
            raise AdelphosException(
                f"remote instance misconfigured {actor_uri}")

        actor_ob = json.loads(ap_actor_res.text)

        gCon.log(f"this is the object {actor_ob}")



