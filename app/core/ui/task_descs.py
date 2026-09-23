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


async def _build_message_ob_str(hmsg, action, task_ob, active_step, t_id):
    task_type = await task_ob().get_scalar('task_type', t_id)
    step_type = active_step.task_step_type
    msg_ob = {
            'mmsg' : f'{action}_{task_type}_{step_type}',
            'hmsg' : hmsg,
            'task_uri' : task_ob().uri.unparse(),
            'active_step' : asdict(active_step),
    }
    return json.dumps(msg_ob)


async def get_dikastes_msg_for_active_step(kernel, task_ob, active_step, t_id):
    task_type = await task_ob().get_scalar("task_type", t_id)
    msg = f"""New task as a judge: {task_type}.
Login to adelphos to mark it completed or deny it."""

    return await _build_message_ob_str(msg, 'dikastes', task_ob, active_step, t_id)


async def get_diakonos_msg_for_active_step(kernel, task_ob, active_step, t_id):
    task_type = await task_ob().get_scalar("task_type", t_id)
    msg =  f"""New task {task_type} to do or to wait."""
    if active_step.data['dikastes_uri'] is not None:
        msg += f"""
The judge for this task is: {active_step.data['dikastes_uri']}.
"""
    msg += """
"""
    return await _build_message_ob_str(msg, 'diakonos', task_ob, active_step, t_id)
    

async def get_diakonos_complete_task_desc(kernel, task_ob, active_step, t_id):
    msg = f"""Completed task or marked completed by the judge.
Thank you for using adelphos."""
    return await _build_message_ob_str(msg, 'complete', task_ob, active_step, t_id)
    

