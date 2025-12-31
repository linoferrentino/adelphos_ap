# this is the dispatcher that understands the Adelphos' API.

from .RequestCtx import RequestCtx
from app.logging import gCon
from app.api.OutgressGateway import post_response
from app.consts import USER_ID
from app.api.AdelphosException import AdelphosException
from app.dao.AliasDto import AliasDto


from argon2 import PasswordHasher

def get_param_safe(ctx, param):
    par_value = ctx.cmd_dict.get(param)
    
    if (par_value is not None):
        return par_value

    raise AdelphosException(f"Required parameter {param} not found")


def alias_create_handler(ctx):

    # first of all let's see if the alias is already present
    alias = get_param_safe(ctx, 'alias')

    ctx.alias = AliasDto.get_from_alias(ctx, alias)

    if (ctx.alias is not None):
        raise AdelphosException(f"Duplicate {alias}, cannot insert")

    # OK! Now I can create a new Alias
    ctx.alias = AliasDto()

    ctx.alias.alias = alias

    clear_pwd = get_param_safe(ctx, 'pwd')

    ph = PasswordHasher()
    
    password_hashed = ph.hash(clear_pwd)

    ctx.alias.password = password_hashed

    ctx.alias.actor_fk = ctx.actor.actor_id

    # OK, let't try to add it to the database
    ctx.alias.store(ctx)

    return f"Created alias {alias} successfully"


def sudo_cmd(func):

    def check_root(ctx):
        pwd = get_param_safe(ctx, 'pwd')
        # I take the hashed password
        hashed = ctx.app.config['General']['root_password']
        #gCon.log(f"check the {hashed} password")
        ph = PasswordHasher()
        try:
            res = ph.verify(hashed, pwd)
        except:
            raise AdelphosException("Wrong sudo password")
        return func(ctx)

    return check_root


@sudo_cmd
def dump_db(ctx):
    ctx.app.dao.dump_database()
    return "dump db OK"


# I have here the command parsers.
cmd_handlers = {
        "alias_create": alias_create_handler,
        "dump_db": dump_db
}


def make_cmd_params(ctx):
    ctx.cmd_dict = {}
    while (len(ctx.cmd_splits) > 1):
        val = ctx.cmd_splits.pop()
        key = ctx.cmd_splits.pop()
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


