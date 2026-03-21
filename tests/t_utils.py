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


from app.logging import gCon
import time
from fastapi.testclient import TestClient
from app.AdelphosApp import get_app
from app.AdelphosApp import del_app

# this generator will be moved in the test module, this is without wait
def generator_test_client(instance_conf, must_wait = False):

    if must_wait:
        #gCon.log("first sleep to let the slave come up")
        time.sleep(1.2)
    client = TestClient(get_app(instance_conf['General']['name'], None, instance_conf))
    with client:
        if must_wait:
            #gCon.log("second sleep to let the root discovery")
            time.sleep(0.5)
        yield client
    del_app()


