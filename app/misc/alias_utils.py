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

import re
from app.core.AdelphosCoreException import AdelphosCoreException
from app.core.ECoreErrno import ECoreErrno


LOCAL_REX = r":local:(\w*)"


def get_local_alias(alias_handle):

    local_user_mt = re.match(LOCAL_REX, alias_handle)
    if local_user_mt is not None:
        local_user = local_user_mt.group(1)
    else:
        local_user = None
    return local_user


def split_alias(alias_name, check = False):

    alias_splits = alias_name.split('.')
    if len(alias_splits) != 2:
        raise AdelphosCoreException(ECoreErrno.EINVALID_ALIAS_SYNTAX, alias_name)

    if check == True:
        alias_check(alias_splits[0])
        alias_check(alias_splits[1])

    return alias_splits


def alias_check(local_name):

    if (re.match("[a-z0-9][a-z0-9_-]*[a-z0-9]+", local_name, 
                 re.IGNORECASE) is None):
        raise AdelphosCoreException(ECoreErrno.EINVALID_ALIAS_SYNTAX,
        f"Invalid name {local_name}, it must begin and end with a letter or a digit.")

    if (len(local_name) < 2 or len(local_name) > 64):
        raise AdelphosCoreException(ECoreErrno.EINVALID_ALIAS_SYNTAX,
        f"name {local_name} length incorrect")



