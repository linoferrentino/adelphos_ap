# this is the dispatcher that understands the Adelphos' API.

# this dispatcher answers to local commands only: remote commands from
# other adelphos instances are dispatched in the remote dispatcher.

from .RequestCtx import RequestCtx
from app.logging import gCon
from app.api.OutgressGateway import post_response
from app.api.OutgressGateway import post_daemon_req
from app.api.OutgressGateway import post_response_inbox
from app.api.OutgressGateway import post_to_actor_inbox
from app.api.params import get_param_safe
from app.api.params import make_cmd_params
from app.ap_api.daemon_qa import daemon_remote_query
from app.ap_api.daemon_qa import daemon_a
from app.ap_api.daemon_qa import daemon_q_handler
from app.ap_api.daemon_qa import daemon_a_handler
from app.consts import USER_ID
from app.api.AdelphosException import AdelphosException
from app.dao.AliasDto import AliasDto
from app.dao.ActorDto import ActorDto
from app.consts import USER_ID
from app.ap_api.AsyncRequest import AsyncGetReq
from fastapi.encoders import jsonable_encoder
import json
import asyncio
import re


from argon2 import PasswordHasher


def validate_local_alias(alias):

    if (re.match("[a-z0-9][a-z0-9_.]+[a-z0-9]+", alias, 
                 re.IGNORECASE) is None):
        raise AdelphosException(f"Invalid alias {alias}, \
it must begin and end with a letter or a digit.")

    if (len(alias) < 2 or len(alias) > 64):
        raise AdelphosException(f"Alias length incorrect")


async def alias_create_handler(ctx):

    # first of all let's see if the alias is lready present
    alias = get_param_safe(ctx, 'alias')
    password = get_param_safe(ctx, 'password')

    host = ctx.app.config['General']['host']
    alias_uri = f"ad1.alias.{alias}@{host}"

    ctx.alias = AliasDto.get_from_alias_uri(ctx, alias_uri)

    if (ctx.alias is not None):
        raise AdelphosException(f"{alias} already existing, cannot insert")

    validate_local_alias(alias)

    # If I am here I can create a new alias
    ctx.alias = AliasDto()

    ctx.alias.alias_uri = alias_uri
    ctx.alias.actor_fk = ctx.actor.actor_uri
    ph = PasswordHasher()
    ctx.alias.password = ph.hash(password)

    # the alias for now has not a password, when we will have p2p
    # encryption then it will be sensible to have one.

    # OK, let't try to add it to the database
    ctx.alias.store(ctx)

    return f"Created alias {alias} successfully.\
Your global identifier in adelphos fediverse is {alias_uri}"


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
        gCon.log(f"But I expect {expected_username}")

        if (total_name != expected_username):
            raise AdelphosException("Invalid username/password")

        return func(ctx)

    return check_root


@sudo_cmd
async def dump_db(ctx):
    ctx.app.dao.dump_database()
    return "dump db OK"


async def tl_create_handler(ctx):
    alias_from = get_param_safe(ctx, 'alias_from')
    alias_to = get_param_safe(ctx, 'alias_to')
    trust = get_param_safe(ctx, 'trust')

    # first of all I have to get the actor from the alias.
    # the alias must be local.
    ctx.alias_from = AliasDto.get_from_alias(ctx, alias_from)
    if (ctx.alias_ob is None):
        raise AdelphosException(f"unknown alias {alias_from}")

    # does the alias belong to the user?
    if (ctx.alias_from.actor_fk != ctx.actor.actor_id):
        raise AdelphosException(
                f"The alias {alias_from} does not belong to you.")

    # OK, now for the outer alias.
    if (alias_to[0] == '#'):
        # this is a remote alias.
        raise AdelphosException(f"implementation to remote alias to do")


    # this is a local alias, so I can create here the trust line, but
    # only if the other alias agrees.
    post_message_to_other_alias(ctx, "do you really want?")
    

    # I have to parse the alias to.

    # remove the dollar.
    #alias_to = alias_to[1:]

    return f"create trust line to {alias_to} initiated, waiting for confirmation"






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
    ctx.daemon = await get_or_discover_actor(ctx, USER_ID, rem_instance)

    # Now I have the daemon.
    gCon.log(f"remote daemon {ctx.daemon.actor_uri} OK")

    # OK, I now have the message to the remote instance
    rcmd = {
            'cmd' : 'echo',
            'msg' : msg
            }
    ctx.daemon_post_ob = rcmd

    await daemon_remote_query(ctx)


# I have here the command handler for the activity pub interface.
cmd_handlers = {
        "alias_create": alias_create_handler,
        "dump_db": dump_db,
        "tl_create": tl_create_handler,
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
    wsctx.actor = await get_or_discover_actor(wsctx, "lino_ferre",
                                          "mastodon.uno")

    gCon.log(f"I have found the remote actor {wsctx.actor}")

    await post_to_actor_inbox(wsctx, "this is a test!")

    return "this is OK!"


# this function is called by activity pub but also by the web sockets.
async def dispatch_request(ctx):
    gCon.rule("--- dispatch request ---")
    gCon.log(f"The message is {ctx.clean_content}")

    # I will have to parse it 
    try:

        await cmd_parse(ctx)

        # I might be in a async context, so I wait for the response:
        # this is done only when we are waiting for a post response.
        if (hasattr(ctx, "async_ctx")):
            gCon.log("I have to wait an async context")
            await ctx.async_ctx

        # If I am here without exceptions I can commit
        if (ctx.need_commit == True):
            gCon.log("I will commit")
            ctx.app.dao.commit()

    except AdelphosException as ex:
        ctx.answer_txt = f"Error! {ex}" 

    # No async, I can give immediately the response
    if (ctx.answer_txt is not None):
        await post_response(ctx)


