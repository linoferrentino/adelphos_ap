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


AP_HOSTNAME_KEY = 'ap_hostname'


class ActivityPubServerModel(BaseIdModel):


    def __init__(self, db):
        super().__init__(db)


    def key_str_from_id(self, numeric_id):
        return f"_ap_srv_${numeric_id}"


    def new_server(self, host_name, forced_id = None):

        server_ob = self._create_base_id(forced_id)

        server_ob[AP_HOSTNAME_KEY] = host_name

        return BaseIdModel.get_id(server_ob)
