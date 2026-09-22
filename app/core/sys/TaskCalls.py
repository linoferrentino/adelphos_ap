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

from app.api.UserSession import active_login
from app.logging import gCon
from app.sdc.Dependencies import Dependencies

from app.core.algo.utils import federated_transaction

import app.core.sys.task_utils as tu
import app.core.sys.family_utils as fu
import app.core.sys.sys_calls_utils as scu

from app.core.model.Tasks import ETaskType, TaskStep

class TaskCalls:

    @staticmethod
    @active_login
    async def _sys_call_accept(kernel, session, pars):
        await _accept_safe(kernel, pars)


    @staticmethod
    @active_login
    async def _sys_call_decline(kernel, session, pars):
        pass


    @staticmethod
    @active_login
    async def _sys_call_first_step(kernel, session, pars):
       return await _task_first_step_safe(kernel, pars)


    @staticmethod
    @active_login
    async def _sys_call_give_hearts(kernel, session, pars):
        await _task_give_hearts_safe(kernel, pars)


@federated_transaction(raise_if_fail = True)
async def _task_give_hearts_safe(kernel, pars, t_id):
    await tu._task_give_hearts_impl(kernel, pars, t_id)


@federated_transaction(raise_if_fail = True)
async def _accept_safe(kernel, pars, t_id):
    await _accept_impl(kernel, pars, t_id)


@federated_transaction(raise_if_fail = True)
async def _task_first_step_safe(kernel, pars, t_id):
    task_uri = pars['task_uri']
    gCon.log(f"first step called {task_uri}")
    return await _first_step_done_impl(kernel, pars, t_id)


async def _first_step_done_impl(kernel, pars, t_id):
    (alias_ob, task_ob, task_type, active_step_idx, steps, active_step) = \
            await _get_active_dikastes_task_for_alias(kernel, pars, t_id)



async def _get_active_dikastes_task_for_alias(kernel, pars, t_id):
    alias_ob = await scu.get_alias_in_session(kernel, pars, t_id)
    task_ob = await tu.get_task_as_dikastes_from_uri(kernel, alias_ob,
                      pars['task_uri'], t_id)
    task_type = await task_ob().get_scalar('task_type', t_id)
    active_step_idx = await task_ob().get_scalar('active_step', t_id)
    steps = await task_ob().get_as_list('steps', t_id)
    active_step_dict = steps[active_step_idx]
    gCon.log(f"active step is {active_step_dict}")
    active_step = TaskStep(**active_step_dict)

    return (alias_ob, task_ob, task_type, active_step_idx, steps, active_step)



async def _accept_impl(kernel, pars, t_id):
    (alias_ob, task_ob, task_type, active_step_idx, steps, active_step) = \
            await _get_active_dikastes_task_for_alias(kernel, pars, t_id)

    stored_pars = active_step.data['pars']
    gCon.log(f"stored_pars {stored_pars}")

    pars = stored_pars | pars

    match task_type:
        case ETaskType.ASSOCIATE_FAMILY:
            await _accept_associate_family(kernel, pars, t_id)
        case _ :
            raise Exception(f"Internal error: task type {task_type} unknown")
    await tu.complete_active_step_for_task(kernel, task_ob, active_step,
                active_step_idx, steps, t_id)


async def _accept_associate_family(kernel, pars, t_id):
    return await fu.family_associate_2nd_half(kernel, pars, t_id)



