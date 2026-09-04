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


from tests.testers.fixtures import simulated_fediverse
import tests.scripts.single_world as sw
from app.logging import gCon

import tests.helpers.root_helpers as rh


def test_simul_root_single(simulated_fediverse):
    sim_fed = simulated_fediverse(sw.single_world_yaml)
    sim_fed.test(sw.fixture_1_single, (
        _test_do_setup
        ))


def _test_do_setup(world):
    gCon.log("doing setup single world")
    ad = world.get_instance('adelphos')
    rh.ws_play_script(ad.get_sock(), 'simple_script')

