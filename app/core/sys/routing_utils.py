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


import secrets
from app.logging import gCon
import app.core.sys.family_utils as fu
import app.core.sys.agora_utils as au


async def distribute_routing_PINs(kernel, offer_uri, chain_exports,
                                 chain_imports, t_id):

    pin_to_give = secrets.randbelow(1000000)
    unlock_pin_needed = secrets.randbelow(1000000)
    pin_to_receive = None
    unlock_pin_to_give = None
    initial_pin = pin_to_give

    gCon.log(f"initial pin is {initial_pin}")

    (pin_to_give, pin_to_receive,
     unlock_pin_needed, unlock_pin_to_give) = await _distribuite_PIN_in_chain(
            kernel, offer_uri, chain_exports, pin_to_give,
            pin_to_receive, unlock_pin_needed, unlock_pin_to_give, t_id)

    await _distribuite_PIN_in_chain(kernel, offer_uri,
            chain_imports, pin_to_give, pin_to_receive, 
            unlock_pin_needed, unlock_pin_to_give, t_id)

    return initial_pin


async def _distribuite_PIN_in_chain(kernel, offer_uri, chain, pin_to_give,
      pin_to_receive, unlock_pin_needed, unlock_pin_to_give, t_id):

    for chain_item in chain:
        agora_ob = await fu.family_get_your_agora(kernel,
                    chain_item, t_id)

        #boss_ob = await fu.family_get_your_boss(kernel,
        #            chain_item, t_id)
        carrier_ob = await au.agora_get_your_carrier(kernel,
                            agora_ob, t_id)

        routing_step = {
            'family_uri' : chain_item().uri.unparse(),
            'pin_to_give' : pin_to_give,
            'pin_to_receive': pin_to_receive,
            'unlock_pin_needed' : unlock_pin_needed,
            'unlock_pin_to_give' : unlock_pin_to_give,
            'offer_uri' : offer_uri,
        }
        #agora_ob().add_scalar('routing_table', routing_step)
        #gCon.log(f"adding routing step {routing_step} to {agora_ob().uri.unparse()}")
        carrier_ob().add_scalar('routing_data', routing_step)
        pin_to_receive = pin_to_give
        pin_to_give = secrets.randbelow(1000000)

        unlock_pin_to_give = unlock_pin_needed
        unlock_pin_needed = secrets.randbelow(1000000)

    return (pin_to_give, pin_to_receive, unlock_pin_needed, unlock_pin_to_give)

