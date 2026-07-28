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

from tests.testers.fixtures import get_routable_app
import tests.adelphoi_test_config as tconf
import tests.helpers.alias_helpers as ah
import tests.helpers.family_helpers as fh
import app.consts as CNST
import app.sdc.standard_conf as stdcnf
from app.exc.AdelphosException import AdErrno


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
            ah.ws_create_user(ws2, 'mary')

            ah.ws_sudo_push_alias(ws1, 'jh.fam1')
            
            fh.ws_invite_user(ws1, f'@mari@{host2}', "X9aa",
                              AdErrno.USER_DOES_NOT_EXIST)
            fh.ws_invite_user(ws1, f'mari@{host2}@invalid', "X9aa",
                              AdErrno.EINVALID_HANDLE)
            fh.ws_invite_user(ws1, f'@mary@{host2}', "X9aa")

  

