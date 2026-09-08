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

import asyncio

from app.federation.FederatedStore import FederatedStore
from app.sdc.Dependencies import Dependencies
from app.logging import gCon


class MockedFederatedStore(FederatedStore):


    def __init__(self, kernel, *, db_type = None, schema = None, start_db =
                 True, stop_db = True):
        super().__init__(kernel, db_type = db_type, schema = schema)
        self._start_db = start_db
        self._stop_db = stop_db


    async def start_async(self):
        await super()._start_async_maybe(self._start_db)
        

    def set_db(self, db):
        gCon.log(f"{id(self)} -> Setting db! {id(db)}")
        self.db = db
 

    async def stop_async(self):
        await super()._stop_async_maybe(self._stop_db)


    def get_db(self):
        return self.db


