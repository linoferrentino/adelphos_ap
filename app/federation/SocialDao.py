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


from abc import abstractmethod, ABC
from app.sdc.Dependency import Dependency
from app.federation.SyncLifespanAware import SyncLifespanAware


class SocialDao(Dependency, SyncLifespanAware):

    def __init__(self, vhost):
        super().__init__(vhost)


    @abstractmethod
    def actor_get(self, server_name, user_name):
        pass


    @abstractmethod
    def actor_get_from_parsed_url(self, parsed_url):
        pass


    @abstractmethod
    def actor_store(self, actor):
        pass


    
