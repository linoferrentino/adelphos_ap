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

# this is the basic class that holds a federated object,
# the federated db is responsible for its life cycle

class FederatedObject:


    def __init__(self, uri, ob):
        self.ref_count = 1
        self.uri = uri
        self.ob = ob

