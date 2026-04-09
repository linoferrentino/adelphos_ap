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

class AdelphosTester:


    @contextlib.contextmanager
    def run_sync(self, adelphos_instance):

        try:

            #db = MemoryStore()
            #ap_mockup = ActivityPubMockup(app.config, db, True)
            #conn_hndl = ConnHandler(app)
            #app.kernel = Adelphos(app.config, app.instance, db, ap_mockup, conn_hndl)
            #ses_worker = asyncio.create_task(session_worker(app))
            #daemon_worker = asyncio.create_task(daemon_bg_cycle(app))
            #app.include_router(ap_mockup.get_async_router())
            #app.include_router(conn_hndl.get_async_router())

            yield 

        finally:

            pass


    def post(self):

        assert 0 == 0

