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
import tests.alias_helpers as ah
import app.consts as CNST
import app.sdc.standard_conf as stdcnf


def test_invite_member(get_routable_app):
    test1 = get_routable_app('test1', stdcnf.release_kernel_template,
                             tconf.adelphos_testable_1_conf)
    test2 = get_routable_app('test2', stdcnf.release_kernel_template,
                             tconf.adelphos_testable_2_conf)

    with test1:
        with test1.websocket_connect(CNST.WS_ROUTE) as ws:
            ah.ws_upgrade_socket_to_local_root(test1, ws,
                                tconf.adelphos_testable_1_conf)
            ah.ws_create_user_alias(ws, 'john', 'jh.fam1', 'pass10')

            ah.ws_sudo_push_alias(ws, 'jh.fam1')
  

