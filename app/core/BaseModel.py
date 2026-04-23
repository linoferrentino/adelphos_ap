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

AD_NAME_KEY = 'name'
AD_ACTOR_ID_KEY = 'actor_id'

from app.dao.AdelphosUri import AdelphosUri
from app.dao.AdelphosUri import uriunparse
from app.dao.AdelphosUri import EAdelphosType

#from app.core.BaseIdModel import BaseIdModel
#from app.core.BaseIdModel import AD_INVALID_ID

# this should be called BaseUriModel, it is the base class
# for the federated objects.
class BaseModel(ABC):


    def __init__(self, fdb, type_val):

        #super().__init__(fdb)
        self.fdb = fdb
        self.type_val = type_val


    def open_name(self, name, family = None, maybe = True):

        uri = self._build_uri(name, family)
        return self.fdb.get_uri_local(uri)


        #ob = self.open_name_id_base(name, family)



    def _build_uri(self, name, family = None):
        uri = AdelphosUri(self.type_val,
            False, None, name = name, family = family)
        return uri


    def _get_uri_key_name(self, name, family = None):

        uri = AdelphosUri(self.type_val,
            False, None, name = name, family = family)

        uri_key = uriunparse(uri)

        return uri_key


    def key_str_from_id(self, numeric_id):

        uri = AdelphosUri(self.type_val,
            True, None, numeric_id = numeric_id)

        uri_key = uriunparse(uri)

        return uri_key


    def open_name_id_base(self, name, family):

        uri_key = self._get_uri_key_name(name, family)

        return self.db.get_maybe(uri_key)


    def create_base(self, name, family = None):

        new_ob = super()._create_base_id()

        uri_name_key = self._get_uri_key_name(name, family)

        new_ob[AD_NAME_KEY] = name

        self.db.set(uri_name_key, new_ob)

        return new_ob



