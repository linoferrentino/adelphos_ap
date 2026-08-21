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


from app.sdc.Dependencies import Dependencies
from app.logging import gCon
from datetime import datetime


async def add_task_to_alias_str(kernel, alias_ob, task, t_id):

    gCon.log(f"[red]Adding {task} to {alias_ob()}[/red]")

    #fdb = kernel.get_dep(Dependencies.FEDERATED_DB)

    #alias_ob = await fdb.uri_read_str(t_id, alias_str, must_lock = True)

    #gCon.log(f"alias is {alias_ob}")

    task_ob = {

            'msg' : task,
            'date' : datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")
    }

    alias_ob().add_scalar('tasks', task_ob)

