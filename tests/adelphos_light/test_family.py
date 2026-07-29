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
import tests.adelphoi_test_config as tconf
import tests.helpers.alias_helpers as ah
import tests.helpers.family_helpers as fh
import app.consts as CNST
import app.sdc.standard_conf as stdcnf
from app.exc.AdelphosException import AdErrno
from app.exc.AdelphosException import AdelphosException
from app.sdc.Dependencies import Dependencies
from app.logging import gCon


def test_invite_member(get_routable_app):
    test1 = get_routable_app('test1', stdcnf.release_kernel_template,
                             tconf.adelphos_testable_1_conf)
    test2 = get_routable_app('test2', stdcnf.release_kernel_template,
                             tconf.adelphos_testable_2_conf)

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

            #fh.ws_accept_invite_raw(


