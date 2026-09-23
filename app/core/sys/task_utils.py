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


import dataclasses
from dataclasses import asdict
from datetime import datetime
import re
import secrets

from app.core.AdelphosCoreException import AdelphosCoreException
from app.core.ECoreErrno import ECoreErrno
from app.core.model.AdelphosUri import AdelphosUri
from app.core.model.AdelphosUri import EAdelphosType
from app.core.model.Tasks import ETaskType, TaskStep, \
        RoutingStepData, FeedbackStepData, RoutingTaskData, ERoutingStepType, \
        EDefaultTaskType, TaskStepData, GenericTaskStepData, FirstStepData, \
        FamilyInviteData

from app.logging import gCon
from app.sdc.Dependencies import Dependencies

import app.core.sys.family_utils as fu
import app.core.sys.social_utils as su
import app.core.sys.sys_calls_utils as scu
import app.core.ui.task_descs as uitk


async def get_task_as_dikastes_from_uri(kernel, alias_ob, task_uri, t_id):
    return await _get_tasks_from_uri(kernel, 'dikastes', alias_ob, task_uri, t_id)


async def get_task_as_diakonos_from_uri(kernel, alias_ob, task_uri, t_id):
    return await _get_tasks_from_uri(kernel, 'diakonos', alias_ob, task_uri, t_id)

    
async def _get_tasks_from_uri(kernel, mode_task, alias_ob, task_uri, t_id):
    tasks = await alias_ob().get_as_list(f'tasks_as_{mode_task}', t_id)
    for task in tasks:
        if task == task_uri:
            fdb = kernel.get_dep(Dependencies.FEDERATED_DB)
            task_ob = await fdb.uri_read_str(t_id, task_uri)
            return task_ob
    raise AdelphosCoreException(ECoreErrno.ETASK_NOT_FOUND,
            f"task {task_uri} not found for {alias_ob().uri.unparse()} as {mode_task}")


def create_step(task_step_type, dikastes_uri, diakonos_uri, pars):
    gCon.log(f"dikastes {dikastes_uri} diakonos {diakonos_uri} create_step with pars {pars}")

    if dataclasses.is_dataclass(pars):
        clean_pars = asdict(pars)
    elif isinstance(pars, dict):
        clean_pars = { k: v for k, v 
                in pars.items() if re.search(r'^_', k) is None }
    else:
        clean_pars = str(pars)

    data = GenericTaskStepData(dikastes_uri, diakonos_uri, clean_pars)
    step = TaskStep(task_step_type, data)

    return step


async def add_associate_family_task(kernel, src_boss_ob, dst_boss_ob,
                                pars, t_id):

    src_boss_uri = src_boss_ob().uri.unparse()
    dst_boss_uri = dst_boss_ob().uri.unparse()

    step = create_step(EDefaultTaskType.DEFAULT_STATE, dst_boss_uri,
                       src_boss_uri, pars)
    steps = []
    steps.append(step)
    task_ob = await create_task(kernel, ETaskType.ASSOCIATE_FAMILY,
                          steps, t_id)



async def _create_first_step(kernel, offer_ob,
                adelphos_from, first_carrier, family_origin, steps, t_id):

    adelphos_to = await offer_ob().get_scalar('adelphos_to', t_id)

    fsd = FirstStepData(first_carrier, adelphos_from)
    step = TaskStep(ERoutingStepType.BEFORE_CARRIER, fsd)
    gCon.log(f"adding first step {step}")

    steps.append(step)


async def _add_last_step(kernel, last_carrier, adelphos_to,
                         steps, family, offer_ob, t_id):
    gCon.log(f"Last step in family {family().uri.unparse()} to {adelphos_to}")
    raise Exception("TODO")


async def _check_create_routing_step(kernel, current_carrier,
            steps, family_ob, offer_ob, t_id):
    new_carrier = await fu.family_get_your_carrier_uri(kernel, family_ob, t_id)
    gCon.log(f"This family has this carrier {new_carrier}")
    if new_carrier == current_carrier:
        gCon.log(f"Nothing to route!")
        return current_carrier

    agora_ob = await fu.family_get_your_agora(kernel, family_ob, t_id)
    agora_uri = agora_ob().uri.unparse()

    gCon.log(f"{current_carrier} will send the object to {new_carrier} in agora {agora_uri}")

    pin_to_give = secrets.randbelow(100000000)

    rsd = RoutingStepData(new_carrier, current_carrier, agora_uri, pin_to_give)

    gCon.log(f"This is the step {rsd}")

    step = TaskStep(ERoutingStepType.ROUTING, rsd)

    steps.append(step)

    return new_carrier


async def add_routing_task(kernel, offer_ob, agora_exported_price,
                           chain_exp, chain_imp, t_id):
    gCon.log(f"add_routing task for {offer_ob().uri.name} {offer_ob().ob.fields}")

    fdb = kernel.get_dep(Dependencies.FEDERATED_DB)
    adelphos_from = await offer_ob().get_scalar('adelphos_from', t_id)
    adelphos_to = await offer_ob().get_scalar('adelphos_to', t_id)

    gCon.log(f"Routing from {adelphos_from} -> {adelphos_to}")

    first_carrier = await fu.family_get_your_carrier_uri(kernel,
                                chain_exp[0], t_id)

    steps = list()
    if first_carrier != adelphos_from:
        gCon.log(f"Adding first step {adelphos_from} != {first_carrier}")
        await _create_first_step(kernel, offer_ob,
                adelphos_from, first_carrier, chain_exp[0], steps, t_id)
    else:
        gCon.log(f"Skipping first step {adelphos_from} == {first_carrier} in family {chain_exp[0]().uri.unparse()}")
    
    current_carrier = first_carrier
    for export_step in chain_exp[1:]:
        current_carrier = await _check_create_routing_step(kernel,
                current_carrier, steps, export_step, offer_ob, t_id)

    for import_step in reversed(chain_imp[:-1]):
        current_carrier = await _check_create_routing_step(kernel,
                current_carrier, steps, import_step, offer_ob, t_id)

    if current_carrier != adelphos_to:
        _add_last_step(kernel, current_carrier, adelphos_to,
                steps, chain_imp[0], offer_ob, t_id)
    else:
        gCon.log(f"Last step is useless. {current_carrier} == {adelphos_to}")

    await _create_give_hearts_step(kernel, adelphos_to, offer_ob,
                                   steps, t_id)

    chain_exp_str = scu.transform_chain_ob_to_str(chain_exp)
    chain_imp_str = scu.transform_chain_ob_to_str(chain_imp)

    rtd = RoutingTaskData(agora_exported_price, chain_exp_str, chain_imp_str)

    gCon.log(f"routing task data {rtd}")

    task_ob = await create_task(kernel, ETaskType.SHIP_OBJECT,
                          steps, t_id, linked_ob = offer_ob, data = rtd)


async def _create_give_hearts_step(kernel, adelphos_to, offer_ob,
            steps, t_id):

    fsd = FeedbackStepData(None, adelphos_to)
    gCon.log(f"adding give feedback step {fsd}")
    step = TaskStep(ERoutingStepType.GIVE_FEEDBACK, fsd)

    steps.append(step)


async def add_invite_to_fediverse_user_task(kernel, alias_ob,
                    user_handle, invite_code, t_id):

    diakonos_uri = alias_ob().uri.unparse()
    fid = FamilyInviteData(None, diakonos_uri, user_handle, invite_code)
    step = TaskStep(EDefaultTaskType.DEFAULT_STATE, fid)

    gCon.log(f"Create the step {step}")

    steps = []
    steps.append(step)

    task_ob = await create_task(kernel, ETaskType.INVITE_FAMILY, steps, t_id)


async def create_task(kernel, task_type, steps, t_id, *,
                linked_ob = None, data = None):

    id_task = secrets.token_hex()
    fdb = kernel.get_dep(Dependencies.FEDERATED_DB)
    task_uri = AdelphosUri(EAdelphosType.TASK_TYPE, str(id_task))

    task_ob = fdb.new_ob_uri(t_id, task_uri, fields = {
         'task_type' : task_type,
         'steps' : steps,
         'created_on' : datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
    })

    if linked_ob is not None:
        await task_ob().set_link('linked_ob', linked_ob, t_id)

    if data is not None:
        task_ob().set_scalar('data', data)

    await task_send_notices_for_active_step(kernel, task_ob, t_id)
    gCon.log(f"created task {task_ob().uri.unparse()}")
    return task_ob


async def task_send_notices_for_active_step(kernel, task_ob, t_id):

    active_step_idx = await task_ob().get_scalar('active_step', t_id)
    steps = await task_ob().get_as_list('steps', t_id)
    active_step_dict = steps[active_step_idx]

    gCon.log(f"active step {active_step_dict} type {type(active_step_dict)}")

    active_step = TaskStep(**active_step_dict)
    fdb = kernel.get_dep(Dependencies.FEDERATED_DB)

    gCon.log(f"active step {active_step} type {type(active_step)}")
    gCon.log(f"active step data {active_step.data} type {type(active_step.data)}")

    dikastes_uri = active_step.data['dikastes_uri']
    if dikastes_uri is not None:
        alias_dikastes_ob = await fdb.uri_read_str(t_id, dikastes_uri)
        alias_dikastes_ob().add_link('tasks_as_dikastes', task_ob)

        msg = await uitk.get_dikastes_msg_for_active_step(kernel,
                    task_ob, active_step, t_id)
        gCon.log(f"sending {msg} to dikastes {dikastes_uri}")
        await su.out_msg_to_alias_ob(kernel, alias_dikastes_ob, msg, t_id)

    diakonos_uri = active_step.data['diakonos_uri']
    alias_diakonos_ob = await fdb.uri_read_str(t_id, diakonos_uri)
     
    alias_diakonos_ob().add_link('tasks_as_diakonos', task_ob)

    msg = await uitk.get_diakonos_msg_for_active_step(kernel,
                    task_ob, active_step, t_id)

    gCon.log(f"sending {msg} to diakonos {diakonos_uri}")
    await su.out_msg_to_alias_ob(kernel, alias_diakonos_ob, msg, t_id)


async def complete_invite_task_for_user(kernel, alias_ob, user_handle,
                                   invite_code, t_id):
    tasks = await alias_ob().get_as_object_list('tasks_as_diakonos', t_id)

    for task_ob in tasks:
        task_type = await task_ob().get_scalar('task_type', t_id)
        gCon.log(f"task is {task_type}")
        if task_type != ETaskType.INVITE_FAMILY:
            continue
        steps = await task_ob().get_as_list('steps', t_id)
        step_zero = steps[0]
        gCon.log(f"step zero is {step_zero}")
        if step_zero['data']['user_handle'] != user_handle:
            continue
        if step_zero['data']['invite_code'] != invite_code:
            continue
        gCon.log(f"Found the task with invite code {invite_code}")
        await alias_ob().remove_link('tasks_as_diakonos', task_ob, t_id)
        return True

    return False


async def complete_active_step_for_task(kernel, task_ob, active_step,
                    active_step_idx, steps, t_id):
    gCon.log(f"Completed step {active_step}")

    active_step_idx += 1
    if len(steps) != active_step_idx:
        task_ob().set_scalar('active_step', active_step_idx)
        await task_send_notices_for_active_step(kernel, task_ob, t_id)

    diakonos_uri = active_step.data['diakonos_uri']
    fdb = kernel.get_dep(Dependencies.FEDERATED_DB)

    alias_diakonos_ob = await fdb.uri_read_str(t_id, diakonos_uri)
    await alias_diakonos_ob().remove_link('tasks_as_diakonos', task_ob, t_id)

    msg = await uitk.get_diakonos_complete_task_desc(kernel, task_ob,
                    active_step, t_id)
    gCon.log(f"send complete msg {msg} to {diakonos_uri}")

    await su.out_msg_to_alias_ob(kernel, alias_diakonos_ob, msg, t_id)

    dikastes_uri = active_step.data['dikastes_uri']
    if dikastes_uri is not None:
        alias_dikastes_ob = await fdb.uri_read_str(t_id, dikastes_uri)
        await alias_dikastes_ob().remove_link('tasks_as_dikastes',
                                              task_ob, t_id)

    steps[active_step_idx-1]['completed_on'] = \
            datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")
    #gCon.log(f"OLD STEP COMPLETED {active_step}")
    task_ob().set_list('steps', steps)
    gCon.log(f"the new steps are {steps}")
 

