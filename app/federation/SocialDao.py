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
from app.exc.AdelphosException import AdelphosException
from app.exc.AdelphosException import AdErrno

from app.logging import gCon
import app.misc.federation_utils as fu


class SocialDao(Dependency, SyncLifespanAware):

    def __init__(self, vhost):
        super().__init__(vhost)


    @abstractmethod
    def actor_get_from_id(self, actor_id):
        pass


    def actor_get_from_actor_handle(self, handle):
        ((preferred_username, rem_instance), actor_instance) = \
                fu.split_social_handle(handle)

        return self.actor_get(rem_instance, preferred_username)


    @abstractmethod
    def actor_get(self, server_name, user_name):
        pass


    @abstractmethod
    def actor_get_from_parsed_url(self, parsed_url):
        pass


    @abstractmethod
    def actor_store(self, actor):
        pass


    
