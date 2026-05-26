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



from abc import ABC
from abc import abstractmethod


class SocialListener(ABC):

    @abstractmethod
    async def new_post(self, sender_id, msg):
        pass
