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


import importlib
import re
from app.core.AdelphosCoreException import AdelphosCoreException
from app.core.ECoreErrno import ECoreErrno
from app.logging import gCon

LOCAL_REX = r":local:(\w*)"

def is_localhost(host_str, this_host = None):
    if ((host_str == this_host) or
        (host_str == '::1') or
        (host_str == 'localhost') or
        (host_str == '127.0.0.1')):
        return True
    return False


# Source - https://stackoverflow.com/a/34963527
# Posted by eugene, modified by community. See post 'Timeline' for change history
# Retrieved 2026-06-19, License - CC BY-SA 4.0
def import_string(dotted_path):
    """
    Import a dotted module path and return the attribute/class designated by the
    last name in the path. Raise ImportError if the import failed.
    """
    try:
        module_path, class_name = dotted_path.rsplit('.', 1)
    except ValueError:
        msg = "%s doesn't look like a module path" % dotted_path
        gCon.log(msg)
        raise Exception(msg)

    module = importlib.import_module(module_path)

    try:
        return getattr(module, class_name)
    except AttributeError:
        msg = 'Module "%s" does not define a "%s" attribute/class' % (
            module_path, class_name)
        gCon.log(msg)
        raise Exception(msg)


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



