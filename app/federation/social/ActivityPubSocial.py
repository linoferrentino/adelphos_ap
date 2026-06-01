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


from app.federation.SimpleSocial import SimpleSocial
from app.logging import gCon
from app.consts import API_POINT
from app.dao.ApActorDto import create_ap_actor
from cryptography.hazmat.primitives import serialization as crypto_serialization
from app.keys import generate_key
from app.sdc.Dependencies import Dependencies


class ActivityPubSocial(SimpleSocial):

    def __init__(self, vhost):
        super().__init__(vhost)


    def _create_user(self, server, user):
        
        preferredusername = user['preferredusername']
        gCon.log(f"creating user {user}")

        user_path = API_POINT + f"/users/{preferredusername}"
        user_inbox = user_path + "/inbox"

        private_key =  user.get('private_key')

        if private_key is None:
            private_key_bytes = generate_key()
        else:
            with open(private_key, "rb") as f:
                private_key_bytes = crypto_serialization.load_pem_private_key(
                        f.read(), password=None)

        gCon.log(f"private key {private_key_bytes}")

        actor = create_ap_actor(server.server_id,
                         user_path, user_inbox, preferredusername,
                                "privateKEY")

        social_dao = self.vhost.get_dep(Dependencies.SOCIAL_DAO)
        actor_dto = social_dao.actor_store(actor)
        gCon.log(f"this is the actor {actor_dto}")


