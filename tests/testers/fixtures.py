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
from tests.testers.SyncGateway import SyncGateway
from tests.transport.sync_mode.loop import stop_loop, get_loop

@pytest.fixture
def sync_gateway():
    get_loop()
    gateway = SyncGateway()
    yield gateway
    stop_loop()


