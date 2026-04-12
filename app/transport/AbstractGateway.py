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

from abc import ABC
from abc import abstractmethod


class AbstractGateway(ABC):


    # these are routed -----> Outbound
    @abstractmethod
    def post_json(self, url, json):
        pass


    @abstractmethod
    def get_json(self, url):
        pass


