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

async def build_message_from_alias(msg, alias_from_uri, alias_to_uri):

    hmsg = f"""

You have received a message from {alias_to_uri}.
The message is: {msg}

Do not reply to this message directy. You can reply to this
message by logging to adelphos and typing this

alias.send_msg alias_to {alias_to_uri} msg '$YOUR_MESSAGE'

"""

    msg_ob = {
            'mmsg' : f'priv_msg',
            'hmsg' : hmsg,
            'alias_from_uri' : alias_from_uri,
            'alias_to_uri' : alias_to_uri,
    }
    return json.dumps(msg_ob)



