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


import httpx
import pytest


import tests.adelphoi_test_config as tconf
from app.sdc.standard_conf import adelphos_standard_configuration
from app.logging import gCon
from tests.testers.fixtures import get_standalone_app
import time


def test_real1(get_standalone_app):
    ad1 = get_standalone_app('adelphos1', tconf.adelphos_stub,
                           adelphos_standard_configuration)

    with ad1:
        time.sleep(1)
        port = tconf.adelphos_stub['General']['port']
        gCon.log(f"I want to connect to port {port}")
        response = httpx.post(f'http://127.0.0.1:{port}/api/users/adelphos/inbox', 
                              json = {'msg' : 'do_all'})
        assert response.status_code == 405


