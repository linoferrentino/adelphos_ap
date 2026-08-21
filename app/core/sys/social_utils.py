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

from app.sdc.Dependencies import Dependencies
from app.logging import gCon


async def out_msg_to_alias_ob(kernel, alias_ob, msg, t_id):


    gCon.log(f"Will send msg {msg}")
    gCon.log(f"to {alias_ob().uri} which is {alias_ob().ob.fields}")
    gCon.log(f"{alias_ob().get_scalar('actor_handle')}")

