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
from app.api.OutgressGateway import post_to_ap_actor_from_local_user
import json
from urllib.parse import urlparse
from app.consts import DAEMON_ID
import re

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


    async def post_to_fediverse_actor(self, sender, fediverse_actor_str, msg):

        # First of all I have to discover the receiver
        (server_rec, actor_rec) = await self.get_or_discover_actor(fediverse_actor_str)

        # If I am here I can send the message!
        res = await post_to_ap_actor_from_local_user(self.app,
                            sender, server_rec, actor_rec, msg)

        return f"s: {res}"


    # this method posts to the fediverse actor a message, the sender is the
    # local adelphos daemon, the recipient is already discovered.
    async def post_to_fediverse_actor_as_daemon(self, server, actor, msg):
        res = await post_to_ap_actor_from_local_user(self.app,
                            DAEMON_ID, server, actor, msg)
        return f"s: {res}"


    # this function will fetch the Fediverse in order to translate a string like
    # @user@host (the classic way to identify a user in Fediverse) into a
    # ApActorDto object.
    # the function will store locally the result, so other queries will fetch
    # the local data.
    # the return of the function is a tuple (server, actor) which identifies
    # this actor in fediverse.
    async def get_or_discover_actor(self, fediverse_actor_str, maybe = False):
        try:
            return await self.get_or_discover_actor_impl(fediverse_actor_str)
        except AdelphosException as adex:
            if (maybe == True):
                gCon.log(f"Got exception while discovering actor {adex}")
                return (None, None)
            raise


    async def get_or_discover_actor_impl(self, fediverse_actor_str):

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

        # this is the server's root.
        server_root = self.app.dao.ap_server_dao.get_or_create_from_host_name(\
                rem_instance)

        gCon.log(f"I have obtained {server_root} as server")

        actor_query = f"https://{rem_instance}/.well-known/webfinger?\
resource=acct:{actor_instance}"

        actor_res = AsyncGetReq(actor_query)
        await self.app.async_req_wait(actor_res)

        if (actor_res.status_code != 200):
            raise AdelphosException(
                    f"remote instance {rem_instance} complains!")

        actor_ob = json.loads(actor_res.text)

        gCon.log(f"The discovery has given me {actor_ob}")

        subject = actor_ob['subject']
        if ( subject != f"acct:{actor_instance}"):
            raise AdelphosException(f"Got {subject} instead!")

        # OK, now we make another query to get his data.
        # I have to get the URI corresponding to activitypub stream
        # this is from W3C reccomentations. 
        # https://www.w3.org/community/reports/socialcg/CG-FINAL-apwf-20240608/
        href_user = None
        for link in actor_ob['links']:
            if link['rel'] != 'self':
                continue
            type_rel = link['type']
            if  ((type_rel == 'application/activity+json') or
                 (type_rel == 'application/ld+json; profile="https://www.w3.org/ns/activitystreams"')):
                href_user = link['href']
                break

        if (href_user is None):
            raise AdelphosException("What? I cannot communicate to this actor")

        # create the parsed key
        key_parsed = urlparse(href_user)
        key_parsed = key_parsed._replace(fragment = "main-key")

        # for now I use the ApActorDao
        actor_root = await self.app.dao.ap_actor_dao.create_from_uri(
                server_root, href_user, key_parsed)
        gCon.log(f"This is the root {actor_root}")

        return (server_root, actor_root)



