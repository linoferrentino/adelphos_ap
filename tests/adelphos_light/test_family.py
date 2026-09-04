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

import re
import pytest

from tests.testers.fixtures import get_routable_app
from tests.testers.fixtures import simulated_fediverse
import tests.adelphoi_test_config as tconf
import tests.helpers.alias_helpers as ah
import tests.helpers.family_helpers as fh
import tests.helpers.object_helpers as oh
import tests.helpers.agora_helpers as agoh
import tests.helpers.task_helpers as tkh
import app.consts as CNST
import app.sdc.standard_conf as stdcnf
from app.exc.AdelphosException import AdErrno
from app.core.ECoreErrno import ECoreErrno
from app.exc.AdelphosException import AdelphosException
from app.sdc.Dependencies import Dependencies
from app.logging import gCon
import tests.scripts.world1 as wld1
import tests.helpers.trust_helpers as th
from app.federation.FederatedObject import str_to_fobs


def test_simul_fediverse_basic(simulated_fediverse):

    sim_fed = simulated_fediverse(wld1.world_1_yaml)
    sim_fed.test(wld1.fixture_1_yaml, (
        _test_put_object_ad,
        _test_associate_with_family_denied,
        _test_list_objects_zero_ok,
        _test_list_objects_zero_ko,
        _test_list_uplevel_ko,
        _test_associate_with_family_ok,
        _test_list_uplevel_one_ok,
        _test_put_object_after_associate,
        _test_list_uplevel_two_ok,
        _test_buy_object_level_one_same_family,
        _test_buy_object_level_one_ok,
        _test_first_task_done_ok,
        ))



def _test_put_object_ad(world):
    ad1 = world.get_instance('ad1')
    ad1.push_user('bob.fam_t1')
    oh.ws_create_object_ad(ad1.get_sock(), 'man sneakers, size 10',
                    12.0 )
    data = oh.ws_create_object_ad(ad1.get_sock(), "a pokemon card", 2)
    gCon.log(f"data is {data}")
    ad1.pop_user()


def _test_put_object_after_associate(world):
    ad2 = world.get_instance('ad2')
    ad2.push_user('katy_al.fam_t2')
    data = oh.ws_create_object_ad(ad2.get_sock(),
                "Lawrence, Son and Lovers", 3.10,
        description = "edition 1995, some marks, but in good condition")
    ad2.pop_user()


def _test_list_objects_zero_ok(world):
    _test_len_get_list(world, 'ad1', 'alice.fam_t1', 2)


def _test_len_get_list(world, instance, user_pushed, len_expected, *,
        code_exp = ECoreErrno.DONE_OK, uplevel = 0, only_uri = True):
    ad1 = world.get_instance(instance)
    ad1.push_user(user_pushed)
    res = agoh.ws_list_ads(ad1.get_sock(), uplevel,
                           code_exp = code_exp, only_uri = only_uri)
    if code_exp == ECoreErrno.DONE_OK:
        list_ads = res['res']
        gCon.log(f"The list is {list_ads}")
        assert len(list_ads) == len_expected
    ad1.pop_user()


def _test_list_objects_zero_ko(world):
    _test_len_get_list(world, 'ad1', 'tom.fam_t2', 0)


def _test_list_uplevel_ko(world):
    _test_len_get_list(world, 'ad1', 'tom.fam_t2', -1, uplevel = 1,
                       code_exp = ECoreErrno.EUPLEVEL_NOT_FOUND)


def _test_associate_with_family_denied(world):
    ad2 = world.get_instance('ad2')
    ad2.push_user('katy_al.fam_t2')
    fh.ws_associate_with_family(ad2.get_sock(), "impossibile", 0.99,
                code_exp = ECoreErrno.EDENIED)
    ad2.pop_user()


def _test_list_uplevel_one_ok(world):
    _test_len_get_list(world, 'ad1', 'alice.fam_t1', 1, uplevel = 1,
                       only_uri = False)


def _test_list_uplevel_two_ok(world):
    _test_len_get_list(world, 'ad1', 'alice.fam_t1', 2, uplevel = 1,
                       only_uri = False)


def _test_first_task_done_ok(world):
    ad2 = world.get_instance('ad2')
    data = ad2.push_user('john_al.fam_t2')
    tasks = data['res']['tasks']
    assert len(tasks) == 0
    ad2.pop_user()

    data = ad2.push_user('katy_al.fam_t2')
    gCon.log(f"data of katy is {data}")
    tasks = data['res']['tasks']
    assert len(tasks) == 1
    gCon.log(f"task of katy is {tasks[0]}")
    pin_to_give = tasks[0]['pars']['pin_to_give']
    gCon.log(f"Pin to give is {pin_to_give}")
    ad2.pop_user()

    ad2.push_user('john_al.fam_t2')
    data = agoh.ws_pin_received(ad2.get_sock(), pin_to_give)
    gCon.log(f"got {data}")
    data = agoh.ws_pin_confirm(ad2.get_sock(), pin_to_give)
    gCon.log(f"got {data}")
    ad2.pop_user()
 

def _test_buy_object_level_one_ok(world):
    gCon.rule("2nd buy, will do it")
    ad1 = world.get_instance('ad1')
    ad1.push_user('alice.fam_t1')
    gCon.rule("2nd buy, first I try a not existent object")
    agoh.ws_buy_object_title(ad1.get_sock(), 1, 'A tale of two cities',
                    code_exp = ECoreErrno.ENO_SUCH_OBJECT)
    gCon.rule("2nd buy, now I ask a real object")
    agoh.ws_buy_object_title(ad1.get_sock(), 1, 'Son and Lovers')
    ad1.pop_user()


def _test_buy_object_level_one_same_family(world):
    gCon.rule("1st buy, same family")
    ad1 = world.get_instance('ad1')
    ad1.push_user('alice.fam_t1')
    agoh.ws_buy_object_title(ad1.get_sock(), 1, 'pokemon', code_exp = 
                    ECoreErrno.ECANNOT_BUY_IN_YOUR_FAMILY )
    ad1.pop_user()


def _test_associate_with_family_ok(world):
    ad2 = world.get_instance('ad2')
    ad2.push_user('john_al.fam_t2')
    fh.ws_associate_with_family(ad2.get_sock(),
                '#fa#fam_t1@www.ad1.com', 1.02,
                location = 'East Of London 33', upper_name =
                                'london_east_33')
    ad2.pop_user()

    ad1 = world.get_instance('ad1')
    alice_inbox = ad1.get_user_inbox('alice')
    assert alice_inbox.count_msg() == 1
    msg = alice_inbox.pop_lst_msg()
    assert re.match("You have a new task associate_family", msg.content) \
            is not None

    data = ad1.push_user('alice.fam_t1')
    gCon.log(f"Data of alice is {data}")
    tasks = data['res']['tasks']
    assert len(tasks) == 1
    assert tasks[0]['task'] == 'associate_family'
    tkh.ws_accept_task(ad1.get_sock(), tasks[0]['id'])
    ad1.pop_user()

    
def test_invite_member(get_routable_app):
    test1 = get_routable_app('test1', stdcnf.release_kernel_template,
                             tconf.adelphos_testable_1_conf)
    test2 = get_routable_app('test2', stdcnf.release_kernel_template,
                             tconf.adelphos_testable_2_conf)

    port1 = tconf.adelphos_testable_1_conf['_port_']
    host1 = f'localhost:{port1}'

    port2 = tconf.adelphos_testable_2_conf['_port_']
    host2 = f'localhost:{port2}'

    with test1, test2:
        with test1.websocket_connect(CNST.WS_ROUTE) as ws1, \
            test2.websocket_connect(CNST.WS_ROUTE) as ws2:

            ah.ws_upgrade_socket_to_local_root(test1, ws1,
                                tconf.adelphos_testable_1_conf)

            ah.ws_upgrade_socket_to_local_root(test2, ws2,
                                tconf.adelphos_testable_2_conf)

            ah.ws_create_user_alias(ws1, 'john', 'jh.fam1', 'pass10')

            social2 = test2.app.routable.get_dep(
                    Dependencies.SOCIAL)
            with pytest.raises(AdelphosException) as adx:
                user_not_existing_inbox = social2.login_user('mary')
            assert adx.value.errno == AdErrno.USER_DOES_NOT_EXIST

            ah.ws_create_user(ws2, 'mary')
            mary_inbox = social2.login_user('mary')
            count_msg = mary_inbox.count_msg()
            assert count_msg == 0

            ah.ws_create_user(ws2, 'mary_friend')
            mary_friend_inbox = social2.login_user('mary_friend')
            count_msg = mary_friend_inbox.count_msg()
            assert count_msg == 0

            ah.ws_sudo_push_alias(ws1, 'jh.fam1')

            code_mary = "c0d3_mar1"
            
            fh.ws_invite_user_raw(ws1, f'@mari@{host2}', code_mary,
                              AdErrno.USER_DOES_NOT_EXIST)
            fh.ws_invite_user_raw(ws1, f'mari@{host2}@invalid', code_mary,
                              AdErrno.EINVALID_HANDLE)
            fh.ws_invite_user_extra_par(ws1, f'@mari@{host2}', code_mary)

            fh.ws_invite_user_macro(ws1, f'@mary@{host2}', code_mary,
                                    mary_inbox)

            alias_chosen = "mary"
            family = "fam1"
            pass_mary = "my_secret_pass"
            gCon.log("==================== accept ===========================")
            fh.ws_accept_invite_raw(ws2, host1, alias_chosen,
                                    family, code_mary, pass_mary, mary_inbox)

            alias_family = f"{alias_chosen}.{family}"
            ah.ws_alias_login(mary_inbox, ws1, alias_family, pass_mary)

            fh.ws_invite_user_raw(ws1, f'@mary_friend@{host2}', 'impossible',
                            ECoreErrno.EDENIED)

