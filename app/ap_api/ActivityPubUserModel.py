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

AP_USER_PATH_KEY = 'ap_user_path'
AP_USER_INBOX_KEY = 'ap_user_inbox'
AP_ACTOR_NAME_KEY = 'ap_actor_name'
AP_PUBLIC_KEY = 'ap_public_key'
AP_IS_DAEMON_KEY = 'ap_is_daemon'


class ActivityPubUserModel(BaseIdModel):


    def __init__(self, db):
        super().__init__(db)


    def key_str_from_id(self, numeric_id):
        return f"_ap_usr_${numeric_id}"


    def new_user(self, server_id, user_path, user_inbox, actor_name,
                 public_key, is_daemon):

        user_ob = self._create_base_id()

        user_ob[AP_USER_PATH_KEY] = user_path
        user_ob[AP_USER_INBOX_KEY] = user_inbox
        user_ob[AP_ACTOR_NAME_KEY] = actor_name
        user_ob[AP_PUBLIC_KEY] = public_key
        user_ob[AP_IS_DAEMON_KEY] = is_daemon

        return BaseIdModel.get_id(user_ob)
