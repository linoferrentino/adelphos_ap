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

# the class that does the sync tester for Adelphos

import contextlib
from tests.TestResponse import TestResponse
from app.transport.AbstractTransport import AbstractTransport
from app.transport.SyncRouter import SyncRouter
from app.store.MemoryStore import MemoryStore
from app.ap_api.ActivityPubMockup import ActivityPubMockup
from app.cli.ConnHandler import ConnHandler
from app.core.Adelphos import Adelphos


# this is the sync equivalent of AdelphosApp class
class AdelphosTester(SyncRouter):


    def __init__(self):
        super().__init__()


    @contextlib.contextmanager
    def run_sync(self, config):

        # I set my host, so that I know the local routes..
        self.host = config['General']['host']

        try:

            # this is the *local* store, adelphos will layer a federated store
            # on top of it.
            db = MemoryStore()
            #ap_mockup = ActivityPubMockup(config, db, True)
            instance_name = config['General']['name']
            kernel = Adelphos(config, instance_name, db, self)
            #conn_hndl = ConnHandler(kernel)
            #ses_worker = asyncio.create_task(session_worker(app))
            #daemon_worker = asyncio.create_task(daemon_bg_cycle(app))
            #app.include_router(ap_mockup.get_async_router())
            #app.include_router(conn_hndl.get_async_router())

            yield 

        finally:

            db.close()


    #def post_json(self, url, json):
    #    assert 0 == 0
    #    return TestResponse(202, None)


    #def get_json(self, url):
    #    return TestResponse(404, None)


