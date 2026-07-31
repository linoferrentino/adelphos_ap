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

from app.consts import ROOT_PATH_DEFAULT
from tests.federation.schema_simple import FIRST_HOST, OTHERHOST
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
def federated_db_local(request):

    def _build_a_federated_db(host, schema_yaml):

        _inline_schema_ = "{}"
        _db_type_ = request.param

        complete_conf = tconf.federated_store_kernel_template.format(
            _inline_schema_ = _inline_schema_,
            _db_type_ = _db_type_,
            _hostname_ = host)

        kernel_conf = yaml.safe_load(complete_conf)

        schema_dict = yaml.safe_load(schema_yaml)

        kernel_conf['modules']['fed_db']['args']['schema'] = schema_dict

        kernel = su.boot_new_kernel('test1', kernel_conf)

        app = SyncApp(host, kernel)
        wrappedapp = SyncTester(app)

        with wrappedapp:
            fdb1_loc = kernel.get_dep(Dependencies.FEDERATED_DB)
            yield fdb1_loc

    return _build_a_federated_db


@pytest.fixture
def fdb1_loc(federated_db_local):

    yield from federated_db_local(FIRST_HOST, schema_simple_yaml)


@pytest.fixture
def fdb_host(federated_db_local):

    def get_db_in_host(host):
        yield from federated_db_local(host, schema_simple_yaml)

    return get_db_in_host



@pytest.fixture(params = ['mem', 'sqlite'])
def federated_db(request):

    def _build_a_federated_db(host, conf_kernel, schema_yaml):

        _inline_schema_ = "{}"
        _db_type_ = request.param

        gCon.log(f"db type {_db_type_}")

        complete_conf = conf_kernel.format(
            _inline_schema_ = _inline_schema_,
            _db_type_ = _db_type_,
            _hostname_ = host)

        kernel_conf = yaml.safe_load(complete_conf)

        schema_dict = yaml.safe_load(schema_yaml)

        kernel_conf['modules']['fed_db']['args']['schema'] = schema_dict

        kernel = su.boot_new_kernel('test1', kernel_conf)

        app = SyncApp(host, kernel, ROOT_PATH_DEFAULT)
        wrappedapp = SyncTester(app)

        return wrappedapp


    return _build_a_federated_db




