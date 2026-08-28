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


async def object_get_field_uri_locked(kernel, ob, field_uri, t_id):
    fdb = kernel.get_dep(Dependencies.FEDERATED_DB)
    uri = ob().get_scalar(field_uri)
    ob_field = await fdb.uri_read_str(t_id, uri, must_lock = True)
    return ob_field
