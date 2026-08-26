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


def family_add_object(fdb, family_ob, object_ob, t_id):
    pass


def ensure_user_boss_in_family(kernel, pars, t_id):
    pass


async def family_get_your_boss(kernel, family_ob, t_id):
    fdb = kernel.get_dep(Dependencies.FEDERATED_DB)
    boss_uri = family_ob().get_scalar('boss')
    boss_ob = await fdb.uri_read_str(t_id, boss_uri, must_lock = True)
    return boss_ob


