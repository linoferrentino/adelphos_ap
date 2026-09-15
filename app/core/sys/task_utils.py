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


import re
from app.sdc.Dependencies import Dependencies
from app.logging import gCon
from datetime import datetime
import app.core.sys.social_utils as su
import uuid

from app.core.AdelphosCoreException import AdelphosCoreException
from app.core.ECoreErrno import ECoreErrno
from app.core.model.AdelphosUri import EAdelphosType
from app.core.model.AdelphosUri import AdelphosUri

from app.core.model.Tasks import ETaskType


async def get_task_with_id(kernel, alias_ob, task_id, t_id):
    tasks = await alias_ob.get_as_list('tasks', t_id)
    for task in tasks:
        if task == task_id:
            gCon.log(f"found! the task")
            fdb = kernel.get_dep(Dependencies.FEDERATED_DB)
            task_ob = await fdb.uri_read_str(t_id, task)
            return task_ob
    raise AdelphosCoreException(ECoreErrno.ETASK_NOT_FOUND, task_id)


def create_step(alias_do_uri, desc_do, alias_check_uri, desc_check, pars):

    gCon.log(f"create_step with pars {pars}")

    if isinstance(pars, dict):
        clean_pars = { k: v for k, v 
                in pars.items() if re.search(r'^_', k) is None }
    else:
        clean_pars = str(pars)

    step = {
            'alias_do' : alias_do_uri,
            'desc_do' : desc_do,
            'alias_check' : alias_check_uri,
            'desc_check' : desc_check,
            'pars' : clean_pars,
    }
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

    task_ob = await create_task(kernel, src_boss_ob, dst_boss_ob,
                          ETaskType.ASSOCIATE_FAMILY,
                          steps, t_id)


async def add_invite_to_fediverse_user_task(kernel, alias_ob,
                    user_handle, invite_code, t_id):

    pars = {
            'user_handle' : user_handle,
            'invite_code' : invite_code,
    }

    step = create_step("", "",
            alias_ob().uri.unparse(),
            f"pending invite for {user_handle} in your family.",  pars)

    steps = []
    steps.append(step)

    task_ob = await create_task(kernel, None, alias_ob, ETaskType.INVITE_FAMILY,
                    steps, t_id)
    


async def create_task(kernel, alias_do, alias_check, task_type, steps, t_id):

    id_task = uuid.uuid4()
    fdb = kernel.get_dep(Dependencies.FEDERATED_DB)
    task_uri = AdelphosUri(EAdelphosType.TASK_TYPE, str(id_task))

    task_ob = fdb.new_ob_uri(t_id, task_uri, fields = {
         'task_type' : task_type,
         'steps' : steps,
         'created_on' : datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
    })

    gCon.log(f"created task {task_ob().uri.unparse()}")
    if alias_do is not None:
        alias_do().add_link('tasks', task_ob)
        desc = steps[0]['desc_do']
        await su.out_msg_to_alias_ob(kernel, alias_do, f"""
You have a new task {task_type} to do: {desc}
Login to adelphos to see its details.""", t_id)
     

    alias_check().add_link('tasks', task_ob)
    desc = steps[0]['desc_check']
    await su.out_msg_to_alias_ob(kernel, alias_check, f"""
You have a new task {task_type} to check: {desc}
Login to adelphos to see its details.""", t_id)

    return task_ob


async def complete_invite_task_for_user(kernel, alias_ob, user_handle,
                                   invite_code, t_id):
    tasks = await alias_ob().get_as_object_list('tasks', t_id)

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
        await alias_ob().remove_link('tasks', task_ob, t_id)
        return True

    return False


async def add_shipping_object_task(kernel, chain_exports, chain_imports, t_id):
    pass


async def add_task_to_alias(kernel, alias_ob, task, pars, t_id):
    if isinstance(pars, dict):
        clean_pars = { k: v for k, v 
                in pars.items() if re.search(r'^_', k) is None }
    else:
        clean_pars = str(pars)

    id_task = uuid.uuid4()

    gCon.log(f"the pars is {pars} clean pars are {clean_pars}")
    task_ob = {
            'id' : str(id_task),
            'task' : task,
            'pars' : clean_pars,
            'date' : datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")
    }

    gCon.log(f"The task is {task_ob} type {type(task_ob)}")

    alias_ob().add_scalar('tasks', task_ob)

    await su.out_msg_to_alias_ob(kernel, alias_ob, f"""
You have a new task {task} 
Login to adelphos to see its details.""", t_id)
 

