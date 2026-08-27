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
    actor_handle = alias_ob().get_scalar('actor_handle')
    social = kernel.get_dep(Dependencies.SOCIAL)
    gCon.log(f"[red]Sending message to {actor_handle}[/red]")
    await social.out_msg_listener_to_handle(actor_handle, msg)


