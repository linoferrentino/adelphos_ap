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
import app.core.sys.ecommerce_utils as ecut
from app.core.ECoreErrno import ECoreErrno
from app.core.AdelphosCoreException import AdelphosCoreException


from app.core.model.Tasks import ETaskType, TaskStep, ERoutingStepType, \
        EDefaultTaskType

from app.core.model.Tasks import RoutingTaskData

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


    @staticmethod
    @active_login
    async def _sys_call_confirm_routing_step(kernel, session, pars):
        return await _task_confirm_routing_step_safe(kernel, pars)


@federated_transaction(raise_if_fail = True)
async def _task_confirm_routing_step_safe(kernel, pars, t_id):
    return await _task_confirm_routing_step_impl(kernel, pars, t_id)


@federated_transaction(raise_if_fail = True)
async def _task_give_hearts_safe(kernel, pars, t_id):
    await _task_give_hearts_impl(kernel, pars, t_id)


@federated_transaction(raise_if_fail = True)
async def _accept_safe(kernel, pars, t_id):
    await _accept_impl(kernel, pars, t_id)


@federated_transaction(raise_if_fail = True)
async def _task_first_step_safe(kernel, pars, t_id):
    return await _first_step_done_impl(kernel, pars, t_id)


async def _task_give_hearts_impl(kernel, pars, t_id):
    (alias_ob, task_ob, active_step_idx, steps, active_step) = \
            await _get_active_diakonos_task_for_alias(kernel, pars, t_id,
                                ETaskType.SHIP_OBJECT, ERoutingStepType.GIVE_FEEDBACK)
    gCon.log(f"alias {alias_ob().uri.unparse()} can give feedback {active_step}")
    data_dict = await task_ob().get_scalar('data', t_id)
    rtd = RoutingTaskData(**data_dict)
    gCon.log(f"The routing task data is {rtd}")

    chain_exp_obs = await scu.reificate_uri_list(kernel, rtd.chain_exports, t_id)
    chain_imp_obs = await scu.reificate_uri_list(kernel, rtd.chain_imports, t_id)

    hearts_given = pars['hearts']
    await ecut.complete_buy_task(kernel, hearts_given,
                        chain_exp_obs, chain_imp_obs, t_id)

    await ecut.distribute_losses_and_gains(kernel, rtd.agora_exported_price,
                chain_exp_obs, chain_imp_obs, ecut.EBMod.CONFIRMED, t_id)

    await tu.complete_active_step_for_task(kernel, task_ob, active_step,
                active_step_idx, steps, t_id)


async def _task_confirm_routing_step_impl(kernel, pars, t_id):
    (alias_ob, task_ob, active_step_idx, steps, active_step) = \
            await _get_active_dikastes_task_for_alias(kernel, pars, t_id,
                        ETaskType.SHIP_OBJECT, ERoutingStepType.ROUTING)

    if active_step.data['pin_to_give'] != pars['pin']:
        raise AdelphosCoreException(ECoreErrno.EWRONG_PIN, "Wrong pin")


    gCon.log(f"alias {alias_ob().uri.unparse()} confirm step!")
    await tu.complete_active_step_for_task(kernel, task_ob, active_step,
                active_step_idx, steps, t_id)


async def _first_step_done_impl(kernel, pars, t_id):
    (alias_ob, task_ob, active_step_idx, steps, active_step) = \
            await _get_active_dikastes_task_for_alias(kernel, pars, t_id,
                                ETaskType.SHIP_OBJECT, ERoutingStepType.BEFORE_CARRIER)


async def _get_active_dikastes_task_for_alias(kernel, pars, t_id, task_type, step_type):
    return await _get_active_task_for_alias_mode(kernel, pars, t_id,
                task_type, step_type, 'dikastes')


async def _get_active_diakonos_task_for_alias(kernel, pars, t_id, task_type, step_type):
    return await _get_active_task_for_alias_mode(kernel, pars, t_id,
                task_type, step_type, 'diakonos')


async def _get_active_task_for_alias_mode(kernel, pars, t_id, task_type, step_type, mode):
    alias_ob = await scu.get_alias_in_session(kernel, pars, t_id)
    task_ob = await tu._get_tasks_from_uri(kernel, mode, alias_ob,
                      pars['task_uri'], t_id)
    task_type_real = await task_ob().get_scalar('task_type', t_id)

    if task_type_real != task_type:
        raise AdelphosCoreException(ECoreErrno.EWRONG_TASK_TYPE,
            f"task {pars['task_uri']} has type {task_type_real} not {task_type}")

    active_step_idx = await task_ob().get_scalar('active_step', t_id)
    steps = await task_ob().get_as_list('steps', t_id)
    active_step_dict = steps[active_step_idx]
    gCon.log(f"active step is {active_step_dict}")
    active_step = TaskStep(**active_step_dict)

    if active_step.task_step_type != step_type:
        raise AdelphosCoreException(ECoreErrno.EWRONG_TASK_STEP,
            f"task {pars['task_uri']} is in step {active_step.task_step_type} \
not {step_type}")

    return (alias_ob, task_ob, active_step_idx, steps, active_step)



async def _accept_impl(kernel, pars, t_id):
    (alias_ob, task_ob, active_step_idx, steps, active_step) = \
            await _get_active_dikastes_task_for_alias(kernel, pars, t_id,
                        ETaskType.ASSOCIATE_FAMILY, EDefaultTaskType.DEFAULT_STATE)

    stored_pars = active_step.data['pars']
    gCon.log(f"stored_pars {stored_pars}")

    pars = stored_pars | pars
    await _accept_associate_family(kernel, pars, t_id)

    await tu.complete_active_step_for_task(kernel, task_ob, active_step,
                active_step_idx, steps, t_id)


async def _accept_associate_family(kernel, pars, t_id):
    return await fu.family_associate_2nd_half(kernel, pars, t_id)



