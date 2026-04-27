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

import traceback

# This is the module which gives services to interact with the Fediverse
# and give to Adelphos the translation to its objects.
from app.api.AdelphosException import AdelphosException
from app.api.AdelphosException import EAdelhposErrno
from app.logging import gCon
from app.ap_api.AsyncRequest import AsyncGetReq
from app.api.OutgressGateway import post_to_ap_actor_from_local_user
import json
from urllib.parse import urlparse
from app.consts import DAEMON_ID
from app.dao.ApActorDto import create_ap_actor
import re


# the API is also able to send and receive answers in fediverse.
class ActivityPubApi:


    # I am initialized with the ActivityPub server.
    def __init__(self, apsrv):
        self.apsrv = apsrv


    # the close might be not needed, in any case I could store messages which
    # have not been submitted, yet.
    def close(self):
        pass


    async def post_to_fediverse_actor(self, sender, fediverse_actor_str, msg):

        # First of all I have to discover the receiver
        (server_rec, actor_rec) = await self.get_or_discover_actor(fediverse_actor_str)

        # If I am here I can send the message!
        await post_to_ap_actor_from_local_user(self.app,
                            sender, server_rec, actor_rec, msg)


    # this method posts to the fediverse actor a message, the sender is the
    # local adelphos daemon, the recipient is already discovered.
    async def post_to_fediverse_actor_as_daemon(self, server, actor, msg):
        await post_to_ap_actor_from_local_user(self.app,
                            DAEMON_ID, server, actor, msg)


    # this function will fetch the Fediverse in order to translate a string like
    # @user@host (the classic way to identify a user in Fediverse) into a
    # ApActorDto object.
    # the function will store locally the result, so other queries will fetch
    # the local data.
    # the return of the function is a tuple (server, actor) which identifies
    # this actor in fediverse.
    def get_or_discover_actor(self, fediverse_actor_str, maybe = False):
        try:
            return self.get_or_discover_actor_impl(fediverse_actor_str)
        except AdelphosException as adex:
            traceback.print_exc()
            if (maybe == True):
                gCon.log(f"Got exception while discovering actor {adex}")
                return (None, None)
            raise


    # this function will fetch the public key of the actor
    def create_from_uri(self, server_dto, actor_uri, key_parsed):

        #gCon.log(f"Create here a cached actor {actor_uri}")

        #res_key = AsyncGetReq(actor_uri)
        res_key = self.apsrv.transport.get_json(actor_uri)
        #await self.dao.app.async_req_wait(res_key)

        if (res_key.status_code != 200):
           raise AdelphosException(
f"Could not fetch the public key {res_key.status_code} {actor_uri}")

        key_ob_text = res_key.body

        key_ob = json.loads(key_ob_text)

        #gCon.log(f"this is the actor {key_ob}")

        pub_key_ob = key_ob['publicKey']

        pub_key_ob_id = pub_key_ob['id']

        # are they the same?
        if (pub_key_ob_id != key_parsed.geturl()):
            raise AdelphosException(f"Error, got {pub_key_ob_id} key \
exp {actor_uri}")

        # is he the owner?
        owner = pub_key_ob['owner'] 
        if (owner != actor_uri):
            gCon.log(f"This is bad {pub_key_ob}")
            gCon.log(f"Error, {owner} different from {actor_uri}")
            raise AdelphosException("Bad key")

        inbox_uri = key_ob['inbox']
        preferred_username = key_ob['preferredUsername']

        # I parse the inbox.
        inbox_parsed = urlparse(inbox_uri)

        # the inbox and the actor uri should belong to the same server,
        # if not there is a problem
        if (inbox_parsed.netloc != key_parsed.netloc):
            raise AdelphosException(
f"Cannot store actor with {inbox_parsed.netloc} != {key_parsed.netloc}")

        
        actor = self.apsrv.ap_actor_dao.get_from_server_path(
                server_dto.server_id, key_parsed.path)
        if actor is not None:
            return actor
        actor = create_ap_actor(server_dto.server_id,
                             key_parsed.path,
                             inbox_parsed.path,
                             preferred_username,
                             pub_key_ob['publicKeyPem'])
        self.apsrv.ap_actor_dao.store(actor)


        #if server_dto.server_id == 0:
        #    #gCon.log("[red]This is a locally defined actor![/red]")
        #else:
        #    # OK, now I can create the actor
        #    actor = create_ap_actor(server_dto.server_id,
        #                     key_parsed.path,
        #                     inbox_parsed.path,
        #                     preferred_username,
        #                     pub_key_ob['publicKeyPem'])
        #    self.apsrv.ap_actor_dao.store(actor)

        # if it is zero it is a locally defined actor, we do not store it
        # because it would violate the db integrity
        #if (server_dto.server_id != 0):
        #else:
        #    local_actor = 
        #gCon.log(f"Created actor {actor}")
        return actor 


    def get_or_discover_actor_impl(self, fediverse_actor_str):

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

        # this is the actor's server 
        server_actor = self.apsrv.ap_server_dao.get_or_create_from_host_name(\
                rem_instance)

        #gCon.log(f"I have obtained {server_actor} as server")

        actor_query = f"https://{rem_instance}/.well-known/webfinger?\
resource=acct:{actor_instance}"

        #actor_res = AsyncGetReq(actor_query)
        #await self.app.async_req_wait(actor_res)


        actor_res = self.apsrv.transport.get_json(actor_query)
        if (actor_res.status_code != 200):
            raise AdelphosException(
                    f"remote instance {rem_instance} complains!",
                    EAdelhposErrno.EREM_ADELPHOS_NOT_FOUND)

        actor_ob = json.loads(actor_res.body)

        #gCon.log(f"The discovery has given me {actor_ob}")

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
        actor_dto = self.create_from_uri(
                server_actor, href_user, key_parsed)
        return (server_actor, actor_dto)



