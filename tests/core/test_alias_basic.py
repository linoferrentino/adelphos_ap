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
from app.core.algo.AdelphosAlgo import AdelphosAlgo 
from app.federation.FederatedStore import FederatedStore
from app.core.model.schema import adelphos_schema_yaml
from app.exc.AdelphosException import AdErrno
import tests.adelphoi_test_config as tconf
from app.logging import gCon
import app.sdc.s_utils as su
from tests.testers.SyncApp import SyncApp
from tests.testers.SyncTester import SyncTester
from app.sdc.Dependencies import Dependencies


@pytest.fixture(params = ['mem', 'sqlite'])
def w_local(request):

    _inline_schema_ = "{}"
    _db_type_ = request.param

    host_name = 'www.h1.com'

    complete_conf = tconf.federated_store_kernel_template.format(
        _inline_schema_ = _inline_schema_,
        _db_type_ = _db_type_,
        _hostname_ = host_name)

    kernel_conf = yaml.safe_load(complete_conf)

    #gCon.log(f"This is the kernel_conf {kernel_conf}")

    schema_dict = yaml.safe_load(adelphos_schema_yaml)

    kernel_conf['modules']['fed_db']['args']['schema'] = schema_dict

    kernel = su.boot_new_kernel('test1', kernel_conf)

    app = SyncApp(host_name, kernel)
    wrappedapp = SyncTester(app)

    with wrappedapp:
        kernel = wrappedapp.get_kernel()
        fdb1_loc = kernel.get_dep(Dependencies.FEDERATED_DB)
        model = AdelphosAlgo(fdb1_loc)
        yield model


def test_add_alias(w_local):

    lino_ob = w_local.alias_algo.alias_create(0, 'lino', 'ferre', 'pass')
    assert lino_ob is not None


def Atest_add_dup_family(w_local):

    lino_ob = w_local.alias_algo.alias_create(0, 'lino', 'ferre', 'pass')
    assert lino_ob is not None
    alice_ob = w_local.alias_algo.alias_create(0, 'alice', 'famal', 'pass99')
    assert alice_ob is not None
    bob_ob = w_local.alias_algo.alias_create(0, 'bob', 'ferre', 'pass')
    assert bob_ob == -AdErrno.EDUPLICATED_FAMILY


def OLDAP_test_login_pass(w_local):


    lino_id = w_local.alias_algo.alias_create(0, 'lino', 'ferre', 'pass')
    res = w_local.alias_algo.login('lino', 'ferre', 'pass')
    assert res == lino_id

    res = w_local.alias_algo.login('lino', 'ferre', 'pass11')
    assert res == -AdErrno.EINVALID_USER_OR_PASSWORD
    res = w_local.alias_algo.login('lino', 'ferre1', 'pass')
    assert res == -AdErrno.EINVALID_USER_OR_PASSWORD
    res = w_local.alias_algo.login('lino1', 'ferre', 'pass')
    assert res == -AdErrno.EINVALID_USER_OR_PASSWORD


