
from app.api.AdelphosException import AdelphosException

def get_param_safe(ctx, param):
    par_value = ctx.cmd_dict.get(param)
    
    if (par_value is not None):
        return par_value

    raise AdelphosException(f"Required parameter {param} not found")

