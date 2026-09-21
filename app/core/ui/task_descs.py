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


async def get_dikastes_msg_for_active_step(kernel, task_ob, active_step, t_id):
    task_type = await task_ob().get_scalar("task_type", t_id)
    return f"""New task as a judge: {task_type}.
Login to adelphos to mark it completed or deny it."""


async def get_diakonos_msg_for_active_step(kernel, task_ob, active_step, t_id):
    task_type = await task_ob().get_scalar("task_type", t_id)
    msg = f"""New task {task_type} to do or to wait."""

    if active_step.data['dikastes_uri'] is not None:
        msg += f"""
The judge for this task is: {active_step.data['dikastes_uri']}.
"""
    return msg

async def get_diakonos_complete_task_desc(kernel, task_ob, active_step, t_id):
    msg = f"""The task {active_step} has been completed.
Thank you for using adelphos."""
    return msg

