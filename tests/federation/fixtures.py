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


import pytest
from tests.federation.schema_simple import LOCALHOST, LOCALHOST1, OTHERHOST
from app.store.MemoryStore import MemoryStore
from app.store.SqliteStore import SqliteStore
from app.federation.FederatedStore import FederatedStore
#from tests.federation.schema_simple import my_test_schema_init
from tests.federation.schema_simple import schema_simple
from app.transport.bridge.loop import run_coro_in_loop


@pytest.fixture(params = ['mem', 'sqlite'])
def fdb1_loc(request):

    if request.param == 'mem':
        db = MemoryStore()
    else:
        db = SqliteStore()

    #fdb = FederatedStore(LOCALHOST, db, my_test_schema_init)
    fdb = FederatedStore(LOCALHOST, db, schema_simple)
    fdb.start()
    return fdb

