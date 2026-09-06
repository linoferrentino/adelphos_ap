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


class TaskCalls:

    @staticmethod
    @active_login
    async def _sys_call_accept(kernel, session, pars):
        task = tu.get_task_with_id(session.get_alias_ob(), pars['task_id'])
        pars['_task'] = task
        pars['_session'] = session
        await TaskCalls._accept_safe(kernel, pars)


    @staticmethod
    @federated_transaction(raise_if_fail = True)
    async def _accept_safe(kernel, pars, t_id):
        await TaskCalls._accept_impl(kernel, pars, t_id)


    @staticmethod
    async def _accept_impl(kernel, pars, t_id):
        task = pars['_task']
        match task['task']:
            case 'associate_family':
                return await TaskCalls._accept_associate_family(
                    kernel, task['pars'], t_id)
            case _ :
                raise Exception(f"Internal error: task type {task['task']} unknown")
        await TaskCalls._remove_task(kernel, pars, task, t_id)


    async def _remove_task(kernel, pars, task, t_id):
        alias_ob = pars['_session'].get_alias_ob()
        tasks = alias_ob.get_as_list('tasks')
        new_list = []
        for task_list in tasks:
            if task_list['id'] != task['id']:
                new_list.append(task_list)
        assert len(tasks) == (len(new_list) + 1)
        alias_ob.set_list('tasks', new_list)
        fdb = kernel.get_dep(Dependencies.FEDERATED_DB)
        fdb.update_detached_ob(t_id, alias_ob)


    @staticmethod
    async def _accept_associate_family(kernel, pars, t_id):
        gCon.log(f"I will accept the task {pars}")
        return await fu.family_associate_2nd_half(kernel, pars, t_id)


    @staticmethod
    @active_login
    async def _sys_call_decline(kernel, session, pars):
        pass


