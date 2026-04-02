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

from app.federation.SocialProvider import SocialProvider


class MemoryAdelphosSocial(SocialProvider):


    def __init__(self):
        self.users = dict()
        self.new_user_id = 0


    def create_user(self, username):
        pass
        

