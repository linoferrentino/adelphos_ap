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

# the Model of an activity pub server

from app.core.BaseIdModel import BaseIdModel


class ActivityPubUserModel(BaseIdModel):


    def __init__(self, db):
        super().__init__(db)


    def key_str_from_id(self, numeric_id):
        return f"_ap_usr_${numeric_id}"


