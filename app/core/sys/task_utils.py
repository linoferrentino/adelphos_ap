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


def get_task_with_id(alias_ob, task_id):
    tasks = alias_ob.get_as_list('tasks')
    for task in tasks:
        if task['id'] == task_id:
            return task
    raise AdelphosCoreException(ECoreErrno.ETASK_NOT_FOUND, task_id)


async def add_task_to_alias(kernel, alias_ob, task, pars, t_id):
    clean_pars = { k: v for k, v 
            in pars.items() if re.search(r'^_', k) is None }

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
You have a new task {task} with parameters {pars}
Login to adelphos to accept it.""", t_id)
 

