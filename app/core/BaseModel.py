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

# The base model of adelphos

from abc import ABC
from abc import abstractmethod

# we do not plan to have more than 2^32-1 objects
AD_INVALID_ID = 0xFFFFFFFF

AD_ID_KEY = 'id'
AD_NAME_KEY = 'name'
AD_ACTOR_ID_KEY = 'actor_id'

from app.dao.AdelphosUri import AdelphosUri
from app.dao.AdelphosUri import uriunparse
from app.dao.AdelphosUri import EAdelphosType

class BaseModel(ABC):


    def __init__(self, db, type_val):
        self.db = db
        self.type_val = type_val
        # the ids start by one: ID 0 is reserved for the local root.
        self.next_id = 1


    @staticmethod
    def get_id(ob):
        return ob[AD_ID_KEY]


    # gets the object by its name, the object is returned as its handle.
    # returns invalid id if not.
    def open_name_id(self, name):
        dto = self.open_name_id_base(name)

        if dto is None:
            return AD_INVALID_ID

        return dto[AD_ID_KEY]


    def _get_uri_key_name(self, name, family = None):

        uri = AdelphosUri(self.type_val,
            False, None, name = name, family = family)

        uri_key = uriunparse(uri)

        return uri_key


    def _get_uri_key_id(self, id_val):
        uri = AdelphosUri(self.type_val,
            True, None, numeric_id = id_val)

        uri_key = uriunparse(uri)

        return uri_key



    def open_name_id_base(self, name):

        uri_key = self._get_uri_key_name(name)

        return self.db.get_maybe(uri_key)


    def create_base(self, name, family = None):

        uri_key = self._get_uri_key_name(name, family)

        ob_id = self.next_id
        self.next_id += 1

        new_ob = {
                AD_ID_KEY: ob_id,
                AD_NAME_KEY: name
                }

        uri_id_key = self._get_uri_key_id(ob_id)

        self.db.set(uri_key, new_ob)
        self.db.set(uri_id_key, new_ob)

        return new_ob


    #def open_uri():
    #    pass


    #def open_id():
    #    pass


    #def create():
    #    pass


    #def update():
    #    pass


    #def delete():
    #    pass


    #def read(field):
    #    pass


    #def as_dict(self):
    #    pass


    #def update_dict():
    #    pass


