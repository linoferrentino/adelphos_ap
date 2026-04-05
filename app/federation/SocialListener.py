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

# the social listener is an object able to accept asynchronous messages from the
# fediverse

from abc import ABC
from abc import abstractmethod


class SocialListener(ABC):


    # the post is already verified!
    @abstractmethod
    async def new_post(self, post):
        pass

