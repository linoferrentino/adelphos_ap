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

def build_msg_login_put_tk(actor_dto, token):

    hmsg = f"""Someone has entered your correct password in adelphos
If it was you, copy in the chat the last line to finalize login, otherwise
please change password immediately. DO NOT SHARE THE TOKEN with anyone.
alias.put_token tk {token}"""

    msg_ob = {
            'mmsg' : f'put_tk',
            'hmsg' : hmsg,
            'logged_alias' : actor_dto.act.preferred_username,
            'token' : token,
    }
    return json.dumps(msg_ob)



