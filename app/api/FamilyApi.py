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

# The family as an objecct.
# 

from app.api.BaseApi import BaseApi

class FamilyApi:

    def __init__(self, gateway):
        super().__init__(gateway, HANDLERS)



# here the handlers for this API
HANDLERS = {
     'assign_currency' : FamilyApi._hndl_assign_currency,
}
