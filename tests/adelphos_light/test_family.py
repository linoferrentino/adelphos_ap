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
import app.consts as CNST
import app.sdc.standard_conf as stdcnf
from app.exc.AdelphosException import AdErrno
from app.exc.AdelphosException import AdelphosException
from app.sdc.Dependencies import Dependencies
from app.logging import gCon
from tests.scripts.world1 import world_1_yaml


def test_create_trust_line(simulated_fediverse):

    sim_fed = simulated_fediverse(world_1_yaml)
    gCon.log(f"world to test is {sim_fed}")

#
#    test1 = get_routable_app('test1', stdcnf.release_kernel_template,
#                             tconf.adelphos_testable_1_conf)
#
#    test2 = get_routable_app('test2', stdcnf.release_kernel_template,
#                             tconf.adelphos_testable_2_conf)
#
#    test3 = get_routable_app('test3', stdcnf.release_kernel_template,
#                             tconf.adelphos_testable_3_conf)
#
#    gCon.log(f"the world is {world_1_yaml}")


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

            ah.ws_sudo_push_alias(ws1, 'jh.fam1')

            code_mary = "c0d3_mar1"
            
            fh.ws_invite_user_raw(ws1, f'@mari@{host2}', code_mary,
                              AdErrno.USER_DOES_NOT_EXIST)
            fh.ws_invite_user_raw(ws1, f'mari@{host2}@invalid', code_mary,
                              AdErrno.EINVALID_HANDLE)

            fh.ws_invite_user_macro(ws1, f'@mary@{host2}', code_mary,
                                    mary_inbox)

            alias_chosen = "mary"
            family = "fam1"
            pass_mary = "my_secret_pass"
            fh.ws_accept_invite_raw(ws2, host1, alias_chosen,
                                    family, code_mary, pass_mary, mary_inbox)

            alias_family = f"{alias_chosen}.{family}"
            ah.ws_alias_login(mary_inbox, ws1, alias_family, pass_mary)

