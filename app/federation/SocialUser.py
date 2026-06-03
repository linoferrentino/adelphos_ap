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


from abc import ABC, abstractmethod


class SocialUser(ABC):

    @abstractmethod
    def count_msg(self):
        pass
    

    @abstractmethod
    def pop_lst_msg(self):
        pass


    @abstractmethod
    async def new_msg(self, sender_id, msg):
        pass



