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
# from app.core.EAdErrno import EAdErrno
# from app.core.AdelphosDao import AdelphosDao
from app.store.MemoryStore import MemoryStore
from app.federation.MemoryAdelphosSocial import MemoryAdelphosSocial
from app.dao.AdelphosDb import AdelphosDb
#from app.core.algo.AdelphosAlgo import AdelphosAlgo 


#from tests.AdelphosTester import AdelphosTester
#from tests.FederationTester import FederationTester

# this is the basic test. Create an adelphos which responds to sync messages
# and is able to create an alias.

import tests.adelphoi_test_config as tconf

@pytest.fixture
def w_local_2():

    tester = AdelphosTester()
    with tester.run_sync(tconf.adelphos_t2_test):
        yield tester


@pytest.fixture
def w_remote_2():

    tester = AdelphosTester()
    with tester.run_sync(tconf.adelphos_remote2_conf):
        yield tester


@pytest.fixture
def federation(w_local_2, w_remote_2):

    federation = FederationTester()
    federation.add_hosts( (w_local_2, w_remote_2) )
    with federation.do_playground():
        yield federation


def OLDAP_test_hello(w_local_2):

    response = w_local_2.post_json('/_backdoor_api_/login', json = { 'user' : 'alice'})
    assert response.status_code == 202


def OLDAP_test_federation(federation):

    response = federation.post_json('https://www.adelphos.it/_backdoor_api_/login', 
                                    json = None)
    assert response.status_code == 202

