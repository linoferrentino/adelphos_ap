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


# must_wait is true when we have to connect to a remote instance.
def generator_test_client(instance_conf, must_wait):

    if must_wait:
        time.sleep(1.2)
    client = TestClient(get_app(instance_conf['General']['name'], None, 
                                instance_conf))
    with client:
        if must_wait:
            time.sleep(0.5)
        yield client
    del_app()


