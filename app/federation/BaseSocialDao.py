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


from app.federation.SocialDao import SocialDao
from cryptography.hazmat.primitives import serialization as crypto_serialization


class BaseSocialDao(SocialDao):

    def __init__(self, vhost):
        super().__init__(vhost)


    def actor_local_get(self, user_name):
        return self.actor_get(self.server_dto, user_name)


    @staticmethod
    def _get_public_key(private_key):
        public_key = private_key.public_key().public_bytes(
                encoding=crypto_serialization.Encoding.PEM,
                format=crypto_serialization.PublicFormat.SubjectPublicKeyInfo)\
                        .decode('utf-8')
        return public_key


    @staticmethod
    def _fill_public_key(actor_dto):

        if actor_dto.public_key is not None:
            return

        private_key = crypto_serialization.load_pem_private_key(
                actor_dto.private_key.encode('utf-8'), password=None)
        public_key = BaseSocialDao._get_public_key(private_key)
        actor_dto.public_key = public_key


