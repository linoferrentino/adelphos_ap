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

from dataclasses import dataclass
from app.logging import gCon
from app.dao.ApServerDto import ApServerDto
from app.dao.ApServerDto import create_ap_server
from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.backends import default_backend as crypto_default_backend
from app.dao.BaseDto import BaseDto


@dataclass
class ApActorImpl(BaseDto):

    actor_id: int
    server_fk: int
    user_path: str
    inbox_path: str
    preferred_username: str
    private_key: str
    public_key: str
    tag: str
    timestamp: str


    def get_pk(self):
        return self.actor_id


    def get_pk_name(self):
        return 'actor_id'


@dataclass
class ApActorDto:

    srv: ApServerDto

    act: ApActorImpl

    cached_private_key: object = None

    cached_public_key: object = None

    def get_inbox(self):
        return f"https://{self.srv.host_name}{self.act.inbox_path}"


    def get_uri(self):
        return f"https://{self.srv.host_name}{self.act.user_path}"


    def get_key_uri(self):
        uri = self.get_uri()
        return f"{uri}#main-key"


    def get_social_handle(self):
        return f"@{self.act.preferred_username}@{self.srv.host_name}"


    @property
    def actor_id(self):
        return self.act.actor_id


    def get_private_key_bytes(self):
        if self.cached_private_key is not None:
            return self.cached_private_key
        if self.act.private_key is None:
            raise Exception("No private key!")
        self.cached_private_key = crypto_serialization.load_pem_private_key(
                        self.act.private_key.encode('utf-8'), password=None)
        return self.cached_private_key


    def _fill_public_key_armored(self):
        private_key = self.get_private_key()
        self.cached_public_key = private_key.public_key()
        self.act.public_key = self.cached_public_key.public_bytes(
            encoding=crypto_serialization.Encoding.PEM,
            format=crypto_serialization.PublicFormat.SubjectPublicKeyInfo)\
                .decode('utf-8')


    def get_public_key_bytes(self):
        if self.cached_public_key is not None:
            return self.cached_public_key
        if self.act.public_key is None:
            self._fill_public_key_armored()
        else:
            self.cached_public_key = crypto_serialization.load_pem_public_key(
                self.act.public_key.encode(),
                backend=crypto_default_backend())
        return self.cached_public_key


def create_local_actor(server_host, user_path, 
                    inbox_path, preferred_username, private_key):

    server_dto = create_ap_server(server_host)

    actor_impl = ApActorImpl(None, None, user_path,
                              inbox_path, preferred_username,
                              private_key, None, None, None)

    actor = ApActorDto(server_dto, actor_impl)
    return actor


def create_remote_actor(server_host, user_path, 
                    inbox_path, preferred_username, public_key):

    server_dto = create_ap_server(server_host)
    actor_impl = ApActorImpl(None, None, user_path,
                              inbox_path, preferred_username,
                              None, public_key, None, None)
    actor = ApActorDto(server_dto, actor_impl)
    return actor 


