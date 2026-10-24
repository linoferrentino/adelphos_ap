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
from app.core.model.Tasks import ETaskType


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

    return await _build_message_ob_str(msg, 'dikastes', task_ob, active_step, t_id)


async def _get_diakonos_msg_for_active_step_impl(kernel, task_ob,
                    active_step, t_id):
    return "TODO _get_diakonos_msg_for_active_step_impl"


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

#    if active_step.data['dikastes_uri'] is not None:
#        msg += f"""
#The dikastes for this task is: {active_step.data['dikastes_uri']}.
#He/she will have to login to adelphos to mark it completed.
#You have to wait or do it.
#"""
#    msg += """
#"""
    return await _build_message_ob_str(msg, 'diakonos', task_ob, active_step, t_id)
    

async def get_diakonos_complete_task_desc(kernel, task_ob, active_step, t_id):
    msg = f"""Completed task or marked completed by the judge.
Thank you for using adelphos."""
    return await _build_message_ob_str(msg, 'complete', task_ob, active_step, t_id)
    

