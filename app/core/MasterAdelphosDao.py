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

# the memory DAO will store the data in memory.

from app.dao.AdelphosDb import AdelphosDb
from app.dao.CurrencyDao import CurrencyDao 
from app.dao.ApServerDao import ApServerDao
from app.dao.ApActorDao import ApActorDao
from app.dao.AdInstanceDao import AdInstanceDao
from app.dao.FamilyDao import FamilyDao
from app.dao.AliasDao import AliasDao

from app.dao.AdelphosUri import EAdelphosType

# A simple container for all the DAOs in the system
class MasterAdelphosDao:


    def __init__(self, app, db_name):
        #gCon.log("Creating the Master DAO, first the connection")
        self.db = AdelphosDb(db_name)
        # I take a reference to the application for the configuration
        self.app = app

        #gCon.log("Creating here the specialized DAOs")

        # I create the specialized DAOs
        self.currency_dao = CurrencyDao(self)
        self.ap_actor_dao  = ApActorDao(self)
        self.ap_server_dao   = ApServerDao(self)
        self.ad_instance_dao = AdInstanceDao(self)
        self.family_dao  = FamilyDao(self)
        self.alias_dao   = AliasDao(self)


    def created_schema_flag(self):
        return self.db.create_schema


    async def uri_factory_str(self, uristr, maybe = False):
        urip = uriparse(uristr)
        return await self.uri_factory(urip, maybe)


    # the get_uri will return a cached version if not present locally and
    # no_route flag is true.
    async def uri_factory(self, uri, no_route = False, maybe = False):
        match uri.obj_type:
            case EAdelphosType.ALIAS_TYPE:
                return await self.alias_dao.get_from_uri(uri, no_route, maybe)
            case _:
                raise AdelphosException(None, EUNKNOW_URI_TYPE)


    def uri_store_cached_str(self, uristr):
        urip = uriparse(uristr)
        return uri_store_cached(urip)


    def uri_store_cached(self, uri):
        match uri.obj_type:
            case EAdelphosType.ALIAS_TYPE:
                return self.alias_dao.store_cached(uri)
            case _:
                raise AdelphosException(None, EUNKNOW_URI_TYPE)


    def close(self):
        self.db.close()


    def commit(self):
        self.db.commit()


    def rollback(self):
        self.db.rollback()

