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
from app.sdc.Dependencies import Dependencies

from tests.testers.SyncApp import SyncApp
from tests.testers.SyncTester import SyncTester

import tests.adelphoi_test_config as tconf
from app.logging import gCon
import app.sdc.s_utils as su


@pytest.fixture(params = ['mem', 'sqlite'])
def fdb1_loc(request):

    _inline_schema_ = "{}"
    _db_type_ = request.param

    complete_conf = tconf.federated_store_kernel_template.format(
        _inline_schema_ = _inline_schema_,
        _db_type_ = _db_type_,
        _hostname_ = LOCALHOST)

    kernel_conf = yaml.safe_load(complete_conf)

    #gCon.log(f"This is the kernel_conf {kernel_conf}")

    schema_dict = yaml.safe_load(schema_simple_yaml)

    kernel_conf['modules']['fed_db']['args']['schema'] = schema_dict

    kernel = su.boot_new_kernel('test1', kernel_conf)

    app = SyncApp(LOCALHOST, kernel)
    wrappedapp = SyncTester(app)

    with wrappedapp:
        kernel = wrappedapp.get_kernel()
        fdb1_loc = kernel.get_dep(Dependencies.FEDERATED_DB)
        yield fdb1_loc


