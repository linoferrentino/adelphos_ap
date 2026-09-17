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



@federated_transaction(raise_if_fail = True)
async def _accept_safe(kernel, pars, t_id):
    await _accept_impl(kernel, pars, t_id)


async def _accept_impl(kernel, pars, t_id):
    session = pars['_param']
    task_ob = await tu.get_task_as_dikastes_with_id(kernel,
                    session.get_alias_ob(), pars['task_id'], t_id)

    gCon.log(f"=== Task is {task_ob().ob.fields}")

    task_type = await task_ob().get_scalar('task_type', t_id)
    active_step_idx = await task_ob().get_scalar('active_step', t_id)
    steps = await task_ob().get_as_list('steps', t_id)
    active_step_dict = steps[active_step_idx]
    gCon.log(f"active step is {active_step_dict}")
    active_step = TaskStep(**active_step_dict)

    match task_type:
        case ETaskType.ASSOCIATE_FAMILY:
            await _accept_associate_family(kernel, active_step.pars, t_id)
        case _ :
            raise Exception(f"Internal error: task type {task_type} unknown")
    #await _remove_task(kernel, pars, task, t_id)
    await tu.complete_active_step_for_task(kernel, task_ob, active_step,
                active_step_idx, steps, t_id)


#async def _remove_task(kernel, pars, task, t_id):
#    alias_ob = pars['_session'].get_alias_ob()
#    tasks = alias_ob.get_as_list('tasks')
#    new_list = []
#    for task_list in tasks:
#        if task_list['id'] != task['id']:
#            new_list.append(task_list)
#    assert len(tasks) == (len(new_list) + 1)
#    alias_ob.set_list('tasks', new_list)
#    fdb = kernel.get_dep(Dependencies.FEDERATED_DB)
#    fdb.update_detached_ob(t_id, alias_ob)
#

async def _accept_associate_family(kernel, pars, t_id):
    return await fu.family_associate_2nd_half(kernel, pars, t_id)



