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
# this is the dispatcher that understands the Adelphos' API.

# this dispatcher answers to local commands only: remote commands from
# other adelphos instances are dispatched in the remote dispatcher.

from app.ap_api.daemon_qa import daemon_a_handler
from app.ap_api.daemon_qa import daemon_q_handler
from app.ap_api.daemon_qa import daemon_remote_query
from app.api.AdelphosException import AdelphosException
from app.api.OutgressGateway import post_response
from app.api.params import get_param_safe
from app.api.params import make_cmd_params
from app.consts import USER_ID
from app.dao.AdelphosUri import uriparse
from app.dao.AliasDto import AliasDto
from app.dao.FamilyDto import FamilyDto
from app.logging import gCon
from argon2 import PasswordHasher
import traceback


def err_middleware(func):

    async def func_safe(ctx):
        try:
            return await func(ctx)

        # in case of exception I will discard everything, so need_commit will be
        # false
        except AdelphosException as err:
            gCon.log(f"{traceback.format_exc()}")
            err_msg = f"Error during command: {str(err)}"
        except Exception as err_ex:
            gCon.log(f"{traceback.format_exc()}")
            err_msg = f"500 Server error during command! We apologize."

        # I won't commit!
        ctx.in_error = True
        return err_msg

    return func_safe 


@err_middleware
async def alias_create_handler(ctx):

    # first of all let's see if the alias is already present
    alias_complete = get_param_safe(ctx, 'alias')
    password = get_param_safe(ctx, 'password')

    host = ctx.app.config['General']['host']

    alias_uri = uriparse(alias_complete)

    if (alias_uri.is_numeric == True):
        raise AdelphosException("Cannot create a numeric alias")

    gCon.log(f"alias uri created {alias_uri}")

    # the family MUST NOT already exist, we cannot create two families in
    # the same instance with the same name.
    family_dto = ctx.app.dao.family_dao.get_from_local_name(alias_uri.family)

    if (family_dto is not None):
        raise AdelphosException(
f"family {alias_uri.family} is already existing in this instance")

    #return "OK, the family is not present, I can proceed"

    # let's create the family, for now it will have only a name, not a currency
    family_dto = FamilyDto(alias_uri.family, 0, None, None)

    family_id = ctx.app.dao.family_dao.store(family_dto)

    # "All OK, I have stored the family"

    # I have now the id of the family and I can create the alias.

    ph = PasswordHasher()
    pass_hashed = ph.hash(password)

    alias_dto = AliasDto(alias_uri.name, 0, family_id, pass_hashed)

    # the alias for now has not a password, when we will have p2p
    # encryption then it will be sensible to have one.

    # OK, let't try to add it to the database
    new_id = ctx.app.dao.alias_dao.store(alias_dto)

    return f"Created alias {alias_dto} successfully, with id {new_id}"


def sudo_cmd(func):

    def check_root(ctx):
        pwd = get_param_safe(ctx, 'pwd')
        # I take the hashed password
        hashed = ctx.app.config['General']['root_password']
        ph = PasswordHasher()
        try:
            res = ph.verify(hashed, pwd)
        except:
            raise AdelphosException("Invalid username/password")

        total_name = f"@{ctx.actor.preferred_username}@{ctx.actor.hostname}"
        gCon.log(f"You would like dump and you are {total_name}")
        expected_username = ctx.app.config['General']['root_user']

        if (total_name != expected_username):
            gCon.log(f"But I expect {expected_username}")
            raise AdelphosException("Invalid username/password")

        return func(ctx)

    return check_root


@err_middleware
@sudo_cmd
async def dump_db(ctx):
    ctx.app.dao.dump_database()
    return "dump db OK"



# this function will query a distant adelphos instance to get an alias, if
# present.
async def rem_alias_get(ctx):
    pass


async def rem_echo_handler(ctx):
    rem_instance = get_param_safe(ctx, "remote-instance")
    msg = get_param_safe(ctx, "msg")

    gCon.log(f"I have to do an echo to @{USER_ID}@{rem_instance}")

    # I have to query the dao to get the remote, in this case (only in this
    # case) the hostname is sufficient to get the actor, because the
    # preferred username is fixed to `daemon'
    ctx.daemon = await ActorDto.get_or_discover_actor(ctx, USER_ID,
                                                       rem_instance)

    # Now I have the daemon.
    gCon.log(f"remote daemon {rem_instance} OK")

    # OK, I now have the message to the remote instance
    rcmd = {
            'cmd' : 'echo',
            'msg' : msg
            }
    ctx.daemon_post_ob = rcmd

    await daemon_remote_query(ctx)


# I have here the command handler for the activity pub interface, actually
# the activity pub interface is very simple.
cmd_handlers = {
        "alias_create": alias_create_handler,
        "dump_db": dump_db,
        "recho": rem_echo_handler,
        "daemon_q": daemon_q_handler, 
        "daemon_a": daemon_a_handler, 
}



async def cmd_parse(ctx):

    # the first string is the @daemon
    ctx.cmd_splits = ctx.clean_content.split()

    mention = ctx.cmd_splits.pop(0)
    if ( mention != f"@{USER_ID}"):
        gCon.log(f"This is not a message for me. {mention}")
        return

    cmd = ctx.cmd_splits.pop(0)

    gCon.log(f"Will do command {cmd}")

    # now the dispatcher.
    handler = cmd_handlers.get(cmd)
    if (handler is None):
        raise AdelphosException(f"command {cmd} not recognized")

    make_cmd_params(ctx)
    ctx.answer_txt = await handler(ctx)


# this context is not a request context, but a web socket context.
async def send_msg_to_alias(wsctx):

    # here I hard code the actor and I try to post to him
    wsctx.actor_dto = await ActorDto.get_or_discover_actor(wsctx, 
                                          "lino_ferre",
                                          "mastodon.uno")

    gCon.log(f"I have found the remote actor {wsctx.actor_dto}")

    await post_to_actor_inbox(wsctx, "this is a test!")

    return "this is OK!"


# this function is called by activity pub but also by the web sockets.
async def dispatch_request(ctx):
    gCon.rule("--- dispatch request ---")
    gCon.log(f"The message is {ctx.clean_content}")

    # Exceptions are captured in the middleware
    await cmd_parse(ctx)

    # I might be in a async context, so I wait for the response:
    # this is done only when we are waiting for a post response.
    if (hasattr(ctx, "async_ctx")):
        gCon.log("I have to wait an async context")
        await ctx.async_ctx

    # If I have arrived here here I can commit, if needed.
    if (ctx.in_error == False):
        gCon.rule("[blue]Commit![/blue]")
        ctx.app.dao.commit()
    else:
        gCon.rule("[red]Rollback![/red]")
        ctx.app.dao.rollback()

    # No async, I can give immediately the response
    if (ctx.answer_txt is not None):
        await post_response(ctx)


