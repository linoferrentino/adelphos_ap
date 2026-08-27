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

    pars = {
      'actor_id' : 0,
      'alias_name' : 'lino',
      'family' : 'ferre',
      'password' : 'pass',
      'user_handle' : '@lino@host.com',
    }

    res = await AliasAlgo.alias_create(kernel, pars)
    assert (res == ECoreErrno.DONE_OK)


def test_add_dup_family(w_local):
    run_coro_in_loop(a_test_add_dup_family, (w_local,))


async def a_test_add_dup_family(w_local):

    kernel = w_local.kernel

    lino_handle = '@lino@host.com'

    pars = {
      'actor_id' : 0,
      'alias_name' : 'lino',
      'family' : 'ferre',
      'password' : 'pass',
      'user_handle' : lino_handle,
    }


    res = await AliasAlgo.alias_create(kernel, pars)
    assert (res == ECoreErrno.DONE_OK)

    pars['alias_name'] = 'alice'
    pars['family'] = 'famal'
    pars['password'] = 'pass99'

    res = await AliasAlgo.alias_create(kernel, pars)
    assert (res == ECoreErrno.DONE_OK)

    pars['alias_name'] = 'bob'
    pars['family'] = 'ferre'
    pars['password'] = 'pass'
    res = await AliasAlgo.alias_create(kernel, pars)
    assert res == -ECoreErrno.EDUPLICATED_FAMILY

    pars = {
      'alias' : 'lino',
      'family' : 'ferre',
      'password' : 'pass',
      'force' : False
    }
    res = await AliasCalls.login(kernel, pars)
    assert res.get_scalar('actor_handle') == lino_handle

    pars['password'] = 'pass1'
    res = await AliasCalls.login(kernel, pars)
    assert res == -ECoreErrno.EINVALID_USER_OR_PASSWORD


    pars['password'] = 'pass'
    pars['alias'] = 'lino1'
    res = await AliasCalls.login(kernel, pars)
    assert res == -ECoreErrno.EINVALID_USER_OR_PASSWORD


