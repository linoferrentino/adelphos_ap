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
from app.core.Adelphos import Adelphos
from app.core.EAdErrno import EAdErrno
from app.core.AdelphosDao import AdelphosDao
from app.store.MemoryStore import MemoryStore
from app.federation.MemoryAdelphosSocial import MemoryAdelphosSocial
from app.dao.AdelphosDb import AdelphosDb
from app.core.algo.AdelphosAlgo import AdelphosAlgo 


from tests.AdelphosTester import AdelphosTester

# this is the basic test. Create an adelphos which responds to sync messages
# and is able to create an alias.

@pytest.fixture
def w_local():

    tester = AdelphosTester()
    with tester.run_sync(None):
        yield tester
    

def test_hello(w_local):

    response = w_local.post('/_backdoor_api_/login', json = { 'user' : 'alice'})
    assert response.status_code == 200
