
from app.api.AdelphosException import AdelphosException


# builds the command dictionary.
def make_cmd_params(ctx):
    ctx.cmd_dict = {}
    while (len(ctx.cmd_splits) > 1):
        val = ctx.cmd_splits.pop()
        key = ctx.cmd_splits.pop()
        ctx.cmd_dict[key] = val


# this function gets the parameter, if not present it gives a default
# or an exception
def get_param_safe(ctx, param, default = None):
    par_value = ctx.cmd_dict.get(param)
    
    if (par_value is not None):
        return par_value

    if (default is not None):
        return default

    raise AdelphosException(f"Required parameter {param} not found and default not given")

