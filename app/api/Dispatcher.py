# this is the dispatcher that understands the Adelphos' API.

from .RequestCtx import RequestCtx
from app.logging import gCon
from app.api.OutgressGateway import post_response
from app.consts import USER_ID
from app.api.AdelphosException import AdelphosException


from argon2 import PasswordHasher

def get_param_safe(ctx, param):
    par_value = ctx.cmd_dict.get(param)
    
    if (par_value is not None):
        return par_value

    raise AdelphosException(f"Required parameter {param} not found")


def alias_create_handler(ctx):

    # The alias is from the dictionary
    ctx.alias.alias = get_param_safe(ctx, 'alias')

    clear_pwd = get_param_safe(ctx, 'pwd')

    ph = PasswordHasher()
    
    password_hashed = ph.hash(clear_pwd)

    ctx.alias.password = password_hashed

    # OK, let't try to add it to the database

    ctx.app.dao.create_alias(ctx)

    return f"Create alias success, your id {ctx.alias.alias_id}"

    


# I have here the command parsers.
cmd_handlers = {
        "alias_create": alias_create_handler,
}

def make_cmd_params(ctx):
    ctx.cmd_dict = {}
    while (len(ctx.cmd_splits) > 1):
        key = ctx.cmd_splits.pop(0)
        val = ctx.cmd_splits.pop(0)
        ctx.cmd_dict[key] = val


def cmd_parse(ctx):

    # the first string is the @daemon
    ctx.cmd_splits = ctx.clean_content.split()

    if (ctx.cmd_splits.pop(0) != f"@{USER_ID}"):
        gCon.log("This is not a message for me.")
        return

    cmd = ctx.cmd_splits.pop(0)

    gCon.log(f"Will do command {cmd}")

    # now the dispatcher.
    handler = cmd_handlers.get(cmd)
    if (handler is None):
        raise AdelphosException(f"command {cmd} not recognized")

    make_cmd_params(ctx)
    ctx.answer_txt = handler(ctx)


async def dispatch_request(ctx):
    gCon.rule("--- dispatch request ---")
    gCon.log(f"The message is {ctx.clean_content}")

    # I will have to parse it 
    try:

        cmd_parse(ctx)

        # If I am here without exceptions I can commit
        if (ctx.need_commit == True):
            gCon.log("I will commit")
            ctx.app.dao.commit()


    except AdelphosException as ex:
        ctx.answer_txt = f"Error! {ex}" 

    post_response(ctx)


