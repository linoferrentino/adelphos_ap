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

# this base class has only an abstract interface which gives to us
# the primary key value and name, useful to update the data.
# this is the ``sister'' class of BaseDao
class BaseDto(ABC):


    @abstractmethod
    def get_pk(self):
        pass


