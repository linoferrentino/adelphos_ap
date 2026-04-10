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

# a simple test response that stores the status code


class TestResponse:


    def __init__(self, status, body):
        self.status_code = status
        self.body = body
