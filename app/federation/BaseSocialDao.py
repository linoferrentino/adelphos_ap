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


from abc import abstractmethod
from app.federation.SocialDao import SocialDao
from cryptography.hazmat.primitives import serialization as crypto_serialization


class BaseSocialDao(SocialDao):

    def __init__(self, vhost):
        super().__init__(vhost)


    #def actor_local_get(self, user_name):
    #    return self.actor_get(self.server_dto, user_name)


    @abstractmethod
    def _srv_get_or_create(self, host_name):
        pass


    @abstractmethod
    def _store_actor_impl(self, actor):
        pass


    @staticmethod
    def _get_public_key(private_key):
        public_key = private_key.public_key().public_bytes(
                encoding=crypto_serialization.Encoding.PEM,
                format=crypto_serialization.PublicFormat.SubjectPublicKeyInfo)\
                        .decode('utf-8')
        return public_key


    @staticmethod
    def _fill_public_key(actor_dto):

        if actor_dto is None:
            return

        if actor_dto.act.public_key is not None:
            return

        private_key = crypto_serialization.load_pem_private_key(
                actor_dto.act.private_key.encode('utf-8'), password=None)
        public_key = BaseSocialDao._get_public_key(private_key)
        actor_dto.act.public_key = public_key


    def actor_store(self, actor):

        server_id = self._srv_get_or_create(actor.srv.host_name)
        BaseSocialDao._fill_public_key(actor)

        actor.srv.server_id = server_id
        actor.act.server_fk = server_id

        actor_id = self._store_actor_impl(actor)
        #actor.act.actor_id = actor_id


