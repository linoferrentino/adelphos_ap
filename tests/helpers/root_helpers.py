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


from app.logging import gCon
import tests.t_utils as tu

from app.exc.AdelphosException import AdErrno


def ws_play_script(ws, script_path, *, code_exp = AdErrno.DONE_OK):
    cmd = f"root.play_script script_path {script_path}"
    tu.ws_send_cmd(ws, cmd, code_exp)


