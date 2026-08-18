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


async def out_msg_to_family_boss(kernel, family_ob, msg, t_id):

    boss_uri = family_ob().get_scalar('boss')
    fdb = kernel.get_dep(Dependencies.FEDERATED_DB)

    boss_ob = await fdb.uri_read_str(t_id, boss_uri)

    gCon.log(f"Will send msg {msg}")
    gCon.log(f"to {boss_uri} which is {boss_ob().get_scalar('actor_id')}")

