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


import pytest
import yaml

from app.store.MemoryStore import MemoryStore
from app.federation.FederatedStore import FederatedStore
from app.core.model.schema import adelphos_schema_yaml
import tests.adelphoi_test_config as tconf
from app.logging import gCon
import app.sdc.s_utils as su
from tests.testers.SyncApp import SyncApp
from tests.testers.SyncTester import SyncTester
from app.sdc.Dependencies import Dependencies

from tests.federation.fixtures import federated_db_local
from app.core.ECoreErrno import ECoreErrno
import threading
from app.core.algo.AliasAlgo import AliasAlgo


@pytest.fixture
def w_local(federated_db_local):
    
    host_name = 'www.h1.com'
    yield from federated_db_local(host_name, adelphos_schema_yaml)


def test_add_alias(w_local):

    kernel = w_local.kernel
    res = AliasAlgo.alias_create(kernel, 0, 'lino', 'ferre', 'pass')
    assert (res == ECoreErrno.DONE_OK)


def test_add_dup_family(w_local):

    kernel = w_local.kernel
    res = AliasAlgo.alias_create(kernel, 0, 'lino', 'ferre', 'pass')
    assert (res == ECoreErrno.DONE_OK)
    res = AliasAlgo.alias_create(kernel, 0, 'alice', 'famal', 'pass99')
    assert (res == ECoreErrno.DONE_OK)
    res = AliasAlgo.alias_create(kernel, 0, 'bob', 'ferre', 'pass')
    assert res == -ECoreErrno.EDUPLICATED_FAMILY


def OLDAP_test_login_pass(w_local):


    lino_id = w_local.alias_algo.alias_create(0, 'lino', 'ferre', 'pass')
    res = w_local.alias_algo.login('lino', 'ferre', 'pass')
    assert res == lino_id

    res = w_local.alias_algo.login('lino', 'ferre', 'pass11')
    assert res == -ECoreErrno.EINVALID_USER_OR_PASSWORD
    res = w_local.alias_algo.login('lino', 'ferre1', 'pass')
    assert res == -ECoreErrno.EINVALID_USER_OR_PASSWORD
    res = w_local.alias_algo.login('lino1', 'ferre', 'pass')
    assert res == -ECoreErrno.EINVALID_USER_OR_PASSWORD


