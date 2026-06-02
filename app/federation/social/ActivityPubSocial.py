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



