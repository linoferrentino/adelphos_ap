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
# This models a place in adelphos, a location in space
# where the users might exchange goods and services.


class PlaceApi:

    # I have the context.
    def __init__(self, ctx):
        self.ctx = ctx


    # Here I can create a place.
    def _hndl_create_place(self, gateway):
        pass


    # edit a place... etc.


    # where can I buy an object? Make a routing?



# here the handlers for this API
HANDLERS = {
     'create_place' : PlaceApi._hndl_create_place
}
