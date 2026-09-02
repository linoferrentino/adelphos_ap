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
from app.core.model.AdelphosUri import EAdelphosType
from app.core.model.AdelphosUri import AdelphosUri


async def alias_get_your_family(kernel, alias_uri_str, t_id):
    fdb = kernel.get_dep(Dependencies.FEDERATED_DB)
    alias_uri = fdb.parse_uri(alias_uri_str)
    family_uri = AdelphosUri(EAdelphosType.FAMILY_TYPE,
            alias_uri.family, host = alias_uri.host)
    family_ob = await fdb.uri_read_ob(t_id, family_uri,
                                      must_lock = True)
    return family_ob


async def alias_get_from_uri(kernel, alias_uri, t_id):
    fdb = kernel.get_dep(Dependencies.FEDERATED_DB)
    alias_ob = await fdb.uri_read_ob(t_id, alias_uri,
                                      must_lock = True)
    return alias_ob



