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
#
# utility functions for the parameters

from app.api.AdelphosException import AdelphosException
from app.logging import gCon
import shlex

# builds the command dictionary, it handles quotes and single quotes 
def make_cmd_params(ctx, command_line):

    parsed_line = shlex.split(command_line)
    ctx.cmd = None
    ctx.cmd_dict = {}
    
    # the first token is the command, the other are the parameters, in key-value
    # pair
    cur_key = None
    for tk in parsed_line:
        if (ctx.cmd is None):
            ctx.cmd = tk
            continue
        if (cur_key is None):
            cur_key = tk
            continue
        # I put the value
        ctx.cmd_dict[cur_key] = tk
        cur_key = None


# this function gets the parameter, if not present it gives a default
# or an exception
def get_param_safe(ctx, param, default = None):
    par_value = ctx.cmd_dict.get(param)
    
    if (par_value is not None):
        return par_value

    if (default is not None):
        return default

    raise AdelphosException(f"Required parameter {param} not found and default not given")

