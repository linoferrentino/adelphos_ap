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


from app.core.ECoreErrno import ECoreErrno
import tests.t_utils as tu


def ws_accept_task(ws, task_id, *, exp_code = ECoreErrno.DONE_OK):
    cmd = f"task.accept task_id {task_id}"
    return tu.ws_send_cmd(ws, cmd, exp_code)
