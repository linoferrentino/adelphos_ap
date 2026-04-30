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


from tests.transport.TRoutable import TRoutable
from tests.testers.SyncApp import SyncApp
from tests.testers.SyncTester import SyncTester


def test_sync_route():

    aroutable = TRoutable()

    app = SyncApp(routes = aroutable)

    test = SyncTester(app)

    response = test.post("inbox/lino", json = { 'msg' : 'do_all' })

    assert response.status_code == 200
    assert response.content == b'Hello lino! do_all'

