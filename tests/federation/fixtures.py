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


import yaml
import pytest

from tests.federation.schema_simple import LOCALHOST, LOCALHOST1, OTHERHOST
from app.store.MemoryStore import MemoryStore
from app.store.SqliteStore import SqliteStore
from app.federation.FederatedStore import FederatedStore
from tests.federation.schema_simple import schema_simple_yaml


@pytest.fixture(params = ['mem', 'sqlite'])
def fdb1_loc(request):

    if request.param == 'mem':
        db = MemoryStore()
    else:
        db = SqliteStore()


    schema_yaml = yaml.safe_load(schema_simple_yaml)
    fdb = FederatedStore(LOCALHOST, db, schema_yaml)

    fdb.start()
    return fdb

