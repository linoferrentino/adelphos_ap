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


import json
import re
import asyncio

from urllib.parse import urlsplit

from app.federation.SocialGateway import SocialGateway
from abc import abstractmethod, ABC
from app.logging import gCon
from starlette.responses import Response
from starlette.exceptions import HTTPException
from app.sdc.Dependencies import Dependencies
from app.exc.AdelphosException import AdelphosException
from app.exc.AdelphosException import AdErrno
from app.dao.ApActorDto import create_remote_actor
import app.misc.federation_utils as fu


class BaseSocialGateway(SocialGateway):

    def __init__(self, kernel):
        super().__init__(kernel)


    async def in_inbox(self, user, request):

        headers = request.headers
        body = await request.body()
        body_str = body.decode()
        #body_str = body
        body_ob = await request.json()

        #gCon.log(f"Request is {request}")
        #gCon.log(f"The body ob is {body_ob} type {type(body_ob)}")
        #gCon.log(f"The body  is {body} type {type(body)}")

        self._filter_message_type(body_ob)

        actor_str = body_ob.get('actor')
        if actor_str is None:
            raise HTTPException(401, "Malformed request, no actor")

        (actor_dto, valid) = await self._check_signature_message(
                actor_str, request, body_str)

        if valid == False:
            raise HTTPException(401, "Invalid signature")
        
        clean_content = await self._parse_message(user, request, actor_str,
                                            body_str, body_ob)

        #content_split = clean_content.split(" ", 1)
        content_split = re.split(r'\s|\n', clean_content, maxsplit = 1)
        if len(content_split) == 1:
            msg = f"Expecting a message with a mention, got {content_split}"
            raise HTTPException(400, msg)

        (mention, rest_of_line) = content_split
        if mention[0] != '@':
            msg = f"Malformed mention {mention}"
            raise HTTPException(400, msg)

        mention = mention[1:]

        #gCon.log(f"The mention is {mention}")

        social = self.kernel.get_dep(Dependencies.SOCIAL)
        local_user= social.local_user_get(mention)

        if local_user is None:
            msg = f"User not found {mention}"
            raise HTTPException(404, msg)

        asyncio.create_task(social.incoming_message(
            actor_dto, local_user,  rest_of_line))
        return Response(status_code=202)


    async def out_outbox(self, actor_from_dto, handle, message):
        actor_to_dto = await self._actor_get_or_discover_from_handle(handle)
        await self.out_outbox_dtos(actor_from_dto, actor_to_dto, message)


    async def out_outbox_dtos(self, actor_from_dto, actor_to_dto, message):
        message = f"@{actor_to_dto.act.preferred_username} {message}"
        (headers, payload_str) = self._do_envelope(
                actor_from_dto, actor_to_dto, message)
        actor_uri = f"https://{actor_to_dto.srv.host_name}\
{actor_to_dto.act.inbox_path}"
        transport = self.kernel.get_dep(Dependencies.TRANSPORT)
        await transport.post_json(actor_uri, payload_str, headers)


    async def discover_user(self, handle):
        actor_dto = await self._actor_get_or_discover_from_handle(handle)
        return actor_dto


    @abstractmethod
    def _do_envelope(self, actor_from_dto, actor_to_dto, message):
        pass


    @abstractmethod
    def _filter_message_type(self, body_ob):
        pass


    @abstractmethod
    async def _parse_message(self, user, request, actor_str, body_str, body_ob):
        pass


    @abstractmethod
    async def _check_signature_message(self, actor_str, request, body_str):
        pass


    async def _actor_get_or_discover_from_handle(self, handle):
        ((preferred_username, rem_instance), actor_instance) = \
                fu.split_social_handle(handle)

        social_dao = self.kernel.get_dep(Dependencies.SOCIAL_DAO)
        gCon.log(f"social dao get {rem_instance} / {preferred_username}")
        actor = social_dao.actor_get(rem_instance, preferred_username)
        if actor is not None:
            return actor

        actor_query = f"https://{rem_instance}/.well-known/webfinger?\
resource=acct:{actor_instance}"

        gCon.log(f"actor query is {actor_query}")

        transport = self.kernel.get_dep(Dependencies.TRANSPORT)
        actor_def_str = await transport.get_json_safe(actor_query, 
                    AdErrno.USER_DOES_NOT_EXIST)
        actor_def_ob = json.loads(actor_def_str)

        subject = actor_def_ob['subject']
        if ( subject != f"acct:{actor_instance}"):
            raise Exception(f"Got {subject} instead!")

        href_user = None
        # I have to get the URI corresponding to activitypub stream
        # this is from W3C reccomendations. 
        # https://www.w3.org/community/reports/socialcg/CG-FINAL-apwf-20240608/
        for link in actor_def_ob['links']:
            if link['rel'] != 'self':
                continue
            type_rel = link['type']
            if  ((type_rel == 'application/activity+json') or
                 (type_rel == 'application/ld+json; profile="https://www.w3.org/ns/activitystreams"')):
                href_user = link['href']
                break

        if (href_user is None):
            raise Exception(f"Misconfigured actor {subject}")

        actor_uri = urlsplit(href_user)

        actor = await self._actor_discover_from_actor_uri(actor_uri)
        return actor


    @staticmethod
    def get_key_uri_from_actor(actor_uri):
        return actor_uri._replace(fragment = "main-key")


    async def _actor_get_or_discover(self, uri):
        actor_uri = urlsplit(uri)
        actor_uri = actor_uri._replace(fragment = "")
        social_dao = self.kernel.get_dep(Dependencies.SOCIAL_DAO)
        actor_dto = social_dao.actor_get_from_parsed_url(actor_uri)
        if actor_dto is not None:
            return actor_dto
        return await self._actor_discover_from_actor_uri(actor_uri)


    async def _actor_discover_from_actor_uri(self, actor_uri_p):

        actor_uri = actor_uri_p.geturl()
        key_parsed = actor_uri_p._replace(fragment = "main-key")

        transport = self.kernel.get_dep(Dependencies.TRANSPORT)
        actor_ob = await transport.get_json_safe(actor_uri,
                AdErrno.USER_DOES_NOT_EXIST)

        key_ob = json.loads(actor_ob)

        pub_key_ob = key_ob['publicKey']
        pub_key_ob_id = pub_key_ob['id']

        if (pub_key_ob_id != key_parsed.geturl()):
            raise Exception(f"Error, got {pub_key_ob_id} key \
exp {actor_uri}")

        owner = pub_key_ob['owner'] 
        if (owner != actor_uri):
            raise Exception(f"Bad key {owner} different from {actor_uri}")

        inbox_uri = key_ob['inbox']
        preferred_username = key_ob['preferredUsername']
        inbox_parsed = urlsplit(inbox_uri)

        social_dao = self.kernel.get_dep(Dependencies.SOCIAL_DAO)

        actor_dto = create_remote_actor(key_parsed.netloc,
                        key_parsed.path, inbox_parsed.path, preferred_username,
                        pub_key_ob['publicKeyPem'])
        social_dao.actor_store(actor_dto)
        return actor_dto


