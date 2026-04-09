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
#


class AdelphosCoreException(Exception):

    def __init__(self, ad_errno, msg = None):
        super().__init__(msg)
        self.errno = ad_errno
