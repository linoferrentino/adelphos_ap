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

from app.core.model.schema import adelphos_schema_yaml
from app.logging import gCon

from tests.federation.fixtures import federated_db_local
from app.core.ECoreErrno import ECoreErrno
from app.core.algo.AliasAlgo import AliasAlgo
from app.core.sys.AliasCalls import AliasCalls
from app.transport.bridge.loop import run_coro_in_loop


@pytest.fixture
def w_local(federated_db_local):
    
    host_name = 'www.h1.com'
    yield from federated_db_local(host_name, adelphos_schema_yaml)


def test_add_alias(w_local):
    run_coro_in_loop(a_test_add_alias, (w_local,))


async def a_test_add_alias(w_local):

    kernel = w_local.kernel
    res = await AliasAlgo.alias_create(kernel, 0, 'lino', 'ferre', 'pass', 1.0)
    assert (res == ECoreErrno.DONE_OK)


def test_add_dup_family(w_local):
    run_coro_in_loop(a_test_add_dup_family, (w_local,))


async def a_test_add_dup_family(w_local):

    kernel = w_local.kernel
    res = await AliasAlgo.alias_create(kernel, 0, 'lino', 'ferre', 'pass', 1.0)
    assert (res == ECoreErrno.DONE_OK)
    res = await AliasAlgo.alias_create(kernel, 0, 'alice', 'famal', 'pass99', 1.0)
    assert (res == ECoreErrno.DONE_OK)
    res = await AliasAlgo.alias_create(kernel, 0, 'bob', 'ferre', 'pass', 1.0)
    assert res == -ECoreErrno.EDUPLICATED_FAMILY
    res = await AliasCalls.login(kernel, 'lino', 'ferre', 'pass', False)
    assert res == ECoreErrno.DONE_OK
    res = await AliasCalls.login(kernel, 'lino', 'ferre', 'pass1', False)
    assert res == -ECoreErrno.EINVALID_USER_OR_PASSWORD
    res = await AliasCalls.login(kernel, 'lino1', 'ferre', 'pass', False)
    assert res == -ECoreErrno.EINVALID_USER_OR_PASSWORD


