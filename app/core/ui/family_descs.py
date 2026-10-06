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

async def build_message_appointed(key, cur_boss, family_uri):

    hmsg = f"""
Hello,
{cur_boss} has appointed you as {key} of family {family_uri}

If this was not intended please contact the root of this instance sending
a message to the administrator. As this:

alias.send_msg alias_to #al#root.admins msg "YOUR_MESSAGE"

"""

    msg_ob = {
            'mmsg' : f'new_{key}',
            'hmsg' : hmsg,
            'former_boss' : cur_boss,
            'family_uri' : family_uri,
    }
    return json.dumps(msg_ob)



