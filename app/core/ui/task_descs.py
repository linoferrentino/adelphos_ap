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

import json
from dataclasses import asdict
from app.logging import gCon
from app.core.model.Tasks import ETaskType, ERoutingStepType, EDefaultTaskType
from app.core.model.AdelphosUri import AdelphosUri
import app.consts as CNST


async def _build_message_ob_str(hmsg, action, task_ob, active_step, t_id):
    task_type = await task_ob().get_scalar('task_type', t_id)
    step_type = active_step.task_step_type
    msg_ob = {
            'mmsg' : f'{action}_{task_type}_{step_type}',
            'hmsg' : hmsg,
            'task_uri' : task_ob().uri.unparse(),
            'active_step' : asdict(active_step),
    }
    return msg_ob


async def _get_dikastes_msg_for_ship_step(kernel, task_ob,
                     active_step, t_id):
    return "_get_dikastes_msg_for_ship_step"


async def _get_dikastes_msg_for_associate_step(kernel, task_ob,
                     active_step, t_id):
    return "_get_dikastes_msg_for_associate_step"


async def _get_dikastes_msg_for_join_step(kernel, task_ob,
                     active_step, t_id):
    return "_get_dikastes_msg_for_join_step"


async def _get_dikastes_msg_for_invite_step(kernel, task_ob,
                     active_step, t_id):
    return "_get_dikastes_msg_for_invite_step"


async def _get_dikastes_msg_for_active_step_impl(kernel, task_ob,
                     active_step, t_id):
    task_type = await task_ob().get_scalar("task_type", t_id)

    match task_type:
        case ETaskType.SHIP_OBJECT:
            return await _get_dikastes_msg_for_ship_step(kernel, task_ob,
                     active_step, t_id)
        case ETaskType.ASSOCIATE_FAMILY:
            return await _get_dikastes_msg_for_associate_step(kernel, task_ob,
                     active_step, t_id)
        case ETaskType.JOIN_FAMILY:
            return await _get_dikastes_msg_for_join_step(kernel, task_ob,
                     active_step, t_id)
        case ETaskType.INVITE_FAMILY:
            return await _get_dikastes_msg_for_invite_step(kernel, task_ob,
                     active_step, t_id)
        case _:
            raise Exception(f"Invalid task type {task_type}")


async def get_dikastes_msg_for_active_step(kernel, task_ob, active_step, t_id):

    step_msg = await _get_dikastes_msg_for_active_step_impl(kernel,
                        task_ob, active_step, t_id)

    msg = f"""Hello, this is adelphos, you are dikastes (Judge) for a new task.
    The task is:
{step_msg}
Login to adelphos to mark it completed or cancel it.
The URI for this task is:
{task_ob().uri.unparse()}
"""
    return await _build_message_ob_str(msg, 'dikastes', task_ob,
                                       active_step, t_id)


async def _get_diakonos_msg_for_ship_step(kernel, task_ob,
                    active_step, t_id):
    active_step_idx = await task_ob().get_scalar('active_step', t_id)
    nsteps = len(await task_ob().get_as_list('steps', t_id))
    gCon.log(f">> active step {active_step}")
    data = active_step.data
    gCon.log(f">> data {data}")

    diakonos = data['diakonos_uri']
    dikastes = data['dikastes_uri']
    object_title = data['object_title']

    step_msg = f"Hello {diakonos},"

    if active_step_idx == 0:
        step_msg += f"""
you have sold the item {object_title}!
"""
    elif active_step_idx == nsteps - 1:
        step_msg += f"""
you should have received the item {object_title}!
"""
    else:
        step_msg += f"""
you have the duty to carry the item {object_title}"""

    step_type = active_step.task_step_type
    match step_type:
        case ERoutingStepType.BEFORE_CARRIER:
            step_msg += f"""
and you have to carry it to the carrier of your family {dikastes} to
be shipped.
"""
        case ERoutingStepType.ROUTING:
            step_msg += f"""to {dikastes}, the carrier
of family {data['family_dest']} for the next routing leg.
You will have to give them the object and the PIN {data['pin_to_give']}.
"""

        case ERoutingStepType.LAST_MILE:
            step_msg += f"""to {dikastes} in your family,
its final destination.
"""

        case ERoutingStepType.GIVE_FEEDBACK:
            task_uri = task_ob().uri.unparse()
            step_msg += f"""
Your next task is to give feeback. You can do it by issuing the following
command in adelphos CLI:

task.give_hearts hearts <number between 0 and 5> task_uri {task_uri}

Remember that hearts from 0 to 2 are a negative feedback.

"""

    return step_msg


async def _get_diakonos_msg_for_invite_step(kernel, task_ob,
                    active_step, t_id):

    data = active_step.data
    diakonos = data['diakonos_uri']
    user_handle = data['user_handle']
    diakonos_uri = data['diakonos_uri']
    invite_code = data['invite_code']
    hostname = kernel.conf().get_host()
    host_family = AdelphosUri.parse(diakonos_uri).family
    
    step_msg = f"""Hello {diakonos},
You have invited to join adelphos by the fediverse user {user_handle} who
is known in adelphos as {diakonos_uri}.

If this seems right to you please send a private mention to adelphos like this:

@{CNST.DAEMON_ID}@{hostname} alias.join_family alias <your_alias> \
        family {host_family} invite_code {invite_code} password <your password>

Please be aware that joining a family means that you will share totally
(100%) its gain and losses. Do it only if you trust the invite.

"""

    return step_msg


async def _get_diakonos_msg_for_associate_step(kernel, task_ob,
                    active_step, t_id):
    return "_get_diakonos_msg_for_associate_step"


async def _get_diakonos_msg_for_join_step(kernel, task_ob,
                    active_step, t_id):
    return "_get_diakonos_msg_for_join_step"


async def _get_diakonos_msg_for_active_step_impl(kernel, task_ob,
                    active_step, t_id):
    task_type = await task_ob().get_scalar("task_type", t_id)

    match task_type:
        case ETaskType.SHIP_OBJECT:
            return await _get_diakonos_msg_for_ship_step(kernel, task_ob,
                     active_step, t_id)
        case ETaskType.ASSOCIATE_FAMILY:
            return await _get_diakonos_msg_for_associate_step(kernel, task_ob,
                     active_step, t_id)
        case ETaskType.JOIN_FAMILY:
            return await _get_diakonos_msg_for_join_step(kernel, task_ob,
                     active_step, t_id)
        case ETaskType.INVITE_FAMILY:
            return await _get_diakonos_msg_for_invite_step(kernel, task_ob,
                     active_step, t_id)
        case _:
            raise Exception(f"Invalid task type {task_type}")



async def get_diakonos_msg_for_active_step(kernel, task_ob, active_step, t_id):

    step_msg = await _get_diakonos_msg_for_active_step_impl(kernel,
                        task_ob, active_step, t_id)

    if active_step.data['dikastes_uri'] is not None:
        dike_msg = f"""The dikastes for this task is 
        {active_step.data['dikastes_uri']}.
        He/she will have to login to adelphos to mark it completed.
        You have to wait or do it."""
    else:
        dike_msg = ""

    msg = f"""Hello, this is adelphos, you have a new task as diakonos.
The task is:
{step_msg}
{dike_msg}
The URI for this task is:
{task_ob().uri.unparse()}
"""
    return await _build_message_ob_str(msg, 'diakonos', task_ob, active_step,
                                       t_id)
    

async def get_diakonos_complete_task_desc(kernel, task_ob, active_step, t_id):
    msg = f"""Completed task or marked completed by the judge.
Thank you for using adelphos."""
    return await _build_message_ob_str(msg, 'complete',
                                       task_ob, active_step, t_id)
    

