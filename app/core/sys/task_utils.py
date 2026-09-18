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
        RoutingStepData, FeedbackStepData, RoutingTaskData

from app.logging import gCon
from app.sdc.Dependencies import Dependencies

import app.core.sys.family_utils as fu
import app.core.sys.social_utils as su
import app.core.sys.sys_calls_utils as scu


async def get_task_as_dikastes_with_id(kernel, alias_ob, task_id, t_id):
    tasks = await alias_ob.get_as_list('tasks_as_dikastes', t_id)
    for task in tasks:
        if task == task_id:
            gCon.log(f"found! the task")
            fdb = kernel.get_dep(Dependencies.FEDERATED_DB)
            task_ob = await fdb.uri_read_str(t_id, task)
            return task_ob
    raise AdelphosCoreException(ECoreErrno.ETASK_NOT_FOUND, task_id)


def create_step(alias_dikastes_uri, desc_dikastes, alias_diakonos_uri,
                desc_diakonos, pars):
    gCon.log(f"dikastes {alias_dikastes_uri} diakonos {alias_diakonos_uri} create_step with pars {pars}")

    if dataclasses.is_dataclass(pars):
        clean_pars = asdict(pars)
    elif isinstance(pars, dict):
        clean_pars = { k: v for k, v 
                in pars.items() if re.search(r'^_', k) is None }
    else:
        clean_pars = str(pars)

    step = TaskStep(alias_dikastes_uri, desc_dikastes,
                alias_diakonos_uri, desc_diakonos, clean_pars)

    return step


async def add_associate_family_task(kernel, src_boss_ob, dst_boss_ob,
                                pars, t_id):

    src_boss_uri = src_boss_ob().uri.unparse()
    dst_boss_uri = dst_boss_ob().uri.unparse()

    step = create_step(dst_boss_uri,
            f"You have a request for associate family from {src_boss_uri}",
            src_boss_uri,
            f"Pending association sent to {dst_boss_uri}.",  pars)

    steps = []
    steps.append(step)

    task_ob = await create_task(kernel, ETaskType.ASSOCIATE_FAMILY,
                          steps, t_id)


async def _create_first_step(kernel, offer_ob,
                adelphos_from, first_carrier, family_origin, steps, t_id):

    desc_object = await offer_ob().get_scalar('description', t_id)
    title_object = await offer_ob().get_scalar('title', t_id)

    adelphos_to = await offer_ob().get_scalar('adelphos_to', t_id)

    desc_dikastes = f"""
{adelphos_from} in your family has sold an item: {title_object}

{desc_object}.

You should take it from your family member and later route it to the upper
agora.

    Mark this task completed ONLY when you have the object in your hands.
    

"""

    desc_diakonos = f"""
You have sold the item {title_object} to {adelphos_to}.

Please bring it to the carrier of your family {first_carrier} as
soon as possible to be shipped.

Happy trading in adelphos!

"""

    step = TaskStep(first_carrier, desc_dikastes,
            adelphos_from, desc_diakonos, None)

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

    rsd = RoutingStepData(agora_uri, pin_to_give)

    gCon.log(f"This is the step {rsd}")

    fdb = kernel.get_dep(Dependencies.FEDERATED_DB)
    desc_object = await offer_ob().get_scalar('description', t_id)
    title_object = await offer_ob().get_scalar('title', t_id)

    desc_dikastes = f"""
You have an object to receive from {current_carrier}.
The title of the object is {title_object}.
Its description is {desc_object}.
{current_carrier} will give to you the PIN: {pin_to_give}

You can mark the task completed ONLY when you have the object
in your hands and you receive the correct PIN. DO NOT share the
PIN with anyone.
"""
    location = await agora_ob().get_scalar('location', t_id)

    desc_diakonos = f"""
You should carry the object {title_object} to {new_carrier}
in the agora {agora_uri}, located on {location}.

You should give to {new_carrier} the object and the PIN {pin_to_give}.

DO NOT share the PIN with anyone and DO NOT give the PIN to
{new_carrier} without the object, or the object without the PIN.

"""

    step = TaskStep(new_carrier, desc_dikastes,
            current_carrier, desc_diakonos, rsd)

    steps.append(step)

    return new_carrier


async def add_routing_task(kernel, offer_ob,
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

    rtd = RoutingTaskData(chain_exp_str, chain_imp_str)

    gCon.log(f"routing task data {rtd}")

    task_ob = await create_task(kernel, ETaskType.SHIP_OBJECT,
                          steps, t_id, linked_ob = offer_ob, data = rtd)


async def _create_give_hearts_step(kernel, adelphos_to, offer_ob,
            steps, t_id):
    token_hearts = secrets.token_urlsafe()
    fsd = FeedbackStepData(token_hearts)

    title_object = await offer_ob().get_scalar('title', t_id)

    desc_diakonos = f"""
You have now the object {title_object}!

Adelphos wishes that you are satisfied.

You should now give a feedback in the form of ``hearts''.
You can give from 0 to 5 hearts, there is not a neutral feedback.

0,1 and 2 hearts are negative (0 the worst)
3,4 and 5 hearts are positive (5 the best)

To do this login to adelphos and issue the following command:

    agora.give_hearts hearts $number_from_0_to_5 token {token_hearts}

Please use your judgement.

"""

    step = TaskStep(None, None,
            adelphos_to, desc_diakonos, fsd)

    steps.append(step)


async def add_invite_to_fediverse_user_task(kernel, alias_ob,
                    user_handle, invite_code, t_id):

    pars = {
            'user_handle' : user_handle,
            'invite_code' : invite_code,
    }

    step = create_step(None, None,
            alias_ob().uri.unparse(),
            f"pending invite for {user_handle} in your family.",  pars)

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

    task_type = await task_ob().get_scalar('task_type', t_id)

    if active_step.alias_dikastes is not None:
        alias_dikastes_ob = await fdb.uri_read_str(t_id,
                                active_step.alias_dikastes)
        alias_dikastes_ob().add_link('tasks_as_dikastes', task_ob)

        desc = active_step.desc_dikastes
        await su.out_msg_to_alias_ob(kernel, alias_dikastes_ob,
f"""
You have a new task {task_type} as a judge: {desc}
Login to adelphos to mark it completed or deny it.""", t_id)

    alias_diakonos_ob = await fdb.uri_read_str(t_id,
                        active_step.alias_diakonos)
     
    alias_diakonos_ob().add_link('tasks_as_diakonos', task_ob)
    desc = active_step.desc_diakonos 

    msg = f"""You have a new task to do or to wait that someone does it,
{task_type}: {desc}.
"""

    if active_step.alias_dikastes is not None:
        msg += f"""
The judge for this task is: {active_step.alias_dikastes}.
"""

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
        if step_zero['pars']['user_handle'] != user_handle:
            continue
        if step_zero['pars']['invite_code'] != invite_code:
            continue
        gCon.log(f"Found the task with invite code {invite_code}")
        await alias_ob().remove_link('tasks_as_diakonos', task_ob, t_id)
        return True

    return False


async def add_shipping_object_task(kernel, chain_exports, chain_imports, t_id):
    pass



async def complete_active_step_for_task(kernel, task_ob, active_step,
                    active_step_idx, steps, t_id):
    gCon.log(f"Completed step {active_step}")
    fdb = kernel.get_dep(Dependencies.FEDERATED_DB)

    alias_diakonos_ob = await fdb.uri_read_str(t_id,
                        active_step.alias_diakonos)
    await alias_diakonos_ob().remove_link('tasks_as_diakonos', task_ob, t_id)

    msg = f"""
The task {active_step.desc_diakonos} has been completed.
Thank you for using adelphos.
"""
    await su.out_msg_to_alias_ob(kernel, alias_diakonos_ob, msg, t_id)

    if active_step.alias_dikastes is not None:
        alias_dikastes_ob = await fdb.uri_read_str(t_id,
                                active_step.alias_dikastes)
        await alias_dikastes_ob().remove_link('tasks_as_dikastes',
                                              task_ob, t_id)
 
    active_step_idx += 1
    if len(steps) == active_step_idx:
        return

    task_ob().set_scalar('active_step', active_step_idx)
    #active_step_dict = steps[active_step_idx]
    #active_step = TaskStep(**active_step_dict)
    #gCon.log(f"The new idx {active_step_idx} is the step {active_step}")

    await task_send_notices_for_active_step(kernel, task_ob, t_id)


 
