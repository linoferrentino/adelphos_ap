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


from app.logging import gCon
from app.exc.AdelphosException import AdelphosException
from app.exc.AdelphosException import AdErrno


def split_social_handle(handle):

    gCon.log(f"searching {handle}")
    (first_char, actor_instance) = (handle[0], handle[1:])

    if (first_char != '@'):
        raise AdelphosException(AdErrno.EINVALID_HANDLE)

    user_host = actor_instance.split('@')
    if (len(user_host) != 2):
        raise AdelphosException(AdErrno.EINVALID_HANDLE)

    return (user_host, actor_instance)


