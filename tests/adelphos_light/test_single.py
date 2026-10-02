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
from tests.testers.fixtures import simulated_fediverse
import tests.scripts.single_world as sw
from app.logging import gCon
from app.core.AdelphosCoreException import AdelphosCoreException
from app.core.ECoreErrno import ECoreErrno

import tests.helpers.root_helpers as rh
import pytest



def test_simul_wrong(simulated_fediverse):
    sim_fed = simulated_fediverse(sw.single_world_yaml)

    fixture_writers_poets_wrong = sw.fixture_writers_poets_parametric.format(
            **sw.fixture_1_writers_poets_vals_ko)

    with pytest.raises(KeyError) as kex:
        sim_fed.test(fixture_writers_poets_wrong, (
            _unreacheable
        ))
    assert str(kex.value) == "'dante'"


def test_send_message_same_net(simulated_fediverse):
    sim_fed = simulated_fediverse(sw.single_world_yaml)

    fixture_writers_poets_good= sw.fixture_writers_poets_parametric.format(
            **sw.fixture_1_writers_poets_vals_ok)

    sim_fed.test(fixture_writers_poets_good, (
        _test_do_send_message
    ))


def _test_do_send_message(world):
    ad = world.get_instance('adelphos')
    rh.ws_play_script(ad.get_sock(), 'send_message_same_net')


def test_simul_root_single(simulated_fediverse):
    sim_fed = simulated_fediverse(sw.single_world_yaml)
    sim_fed.test(sw.fixture_1_single, (
        _test_do_setup
        ))


def _test_do_setup(world):
    ad = world.get_instance('adelphos')
    rh.ws_play_script(ad.get_sock(), 'simple_script')


def test_simul_complex_wrong_boss(simulated_fediverse):
    sim_fed = simulated_fediverse(sw.single_world_yaml)
    fixture_2_complex = sw.fixture_2_complex_parametric.format(
            **sw.fixture_2_complex_wrong_boss
    )
    with pytest.raises(AdelphosCoreException) as acex:
        sim_fed.test(fixture_2_complex, (
            _unreacheable,
        ))
    assert acex.value.errno == ECoreErrno.EEXTERNAL_ALIAS


def test_simul_complex_wrong_carrier(simulated_fediverse):
    sim_fed = simulated_fediverse(sw.single_world_yaml)
    fixture_2_complex = sw.fixture_2_complex_parametric.format(
            **sw.fixture_2_complex_wrong_carrier
    )
    with pytest.raises(AdelphosCoreException) as acex:
        sim_fed.test(fixture_2_complex, (
            _unreacheable,
        ))
    assert acex.value.errno == ECoreErrno.EEXTERNAL_ALIAS
    assert re.search('#al#c1.f1_l0', acex.value.out_str) is not None


def _unreacheable(world):
    assert False


def test_simul_complex(simulated_fediverse):
    sim_fed = simulated_fediverse(sw.single_world_yaml)
    fixture_2_complex = sw.fixture_2_complex_parametric.format(
            **sw.fixture_2_complex_ok_vals
    )
    
    sim_fed.test(fixture_2_complex, (
        _test_add_objects,
        _test_check_calculations,
    ))


def _test_add_objects(world):
    ad = world.get_instance('adelphos')
    rh.ws_play_script(ad.get_sock(), 'add_objects')


def _test_check_calculations(world):
    ad = world.get_instance('adelphos')
    rh.ws_play_script(ad.get_sock(), 'check_calcs')


