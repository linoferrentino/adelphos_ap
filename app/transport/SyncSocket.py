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



# a class that models a bidirectional socket using simple functions
class SyncSocket__OLD:


    def __init__(self, ob_server):
        self.server = ob_server


    # the receive is not needed, because all communication is
    # from client to server, 1:1 messages.
    def send(self, text):
        pass
