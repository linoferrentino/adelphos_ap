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

# the base id model is the base class that models an object
# in our db with a numeric id.

from abc import ABC, abstractmethod

AD_ID_KEY = 'id'

# we do not plan to have more than 2^32-1 objects
AD_INVALID_ID = 0xFFFFFFFF


# this is a class that models an object with an id.
class BaseIdModel(ABC):


    def __init__(self, db):
        # id 0 is reserved.
        self.db = db
        self.next_id = 1


    @staticmethod
    def get_id(ob):
        return ob[AD_ID_KEY]


    @abstractmethod
    def key_str_from_id(self, numeric_id):
        pass



    def _create_base_id(self, forced_id = None):

        if forced_id is None:
            ob_id = self.next_id
            self.next_id += 1
        else:
            ob_id = forced_id

        new_ob = {
                AD_ID_KEY: ob_id,
                }

        uri_id_key = self.key_str_from_id(ob_id)

        self.db.set(uri_id_key, new_ob)

        return new_ob


