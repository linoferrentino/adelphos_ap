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
from app.dao.AliasDto import AliasDao
from app.dao.ActorDto import ActorDto
from app.dao.AdelphosUri import uriparse
from app.dao.AdelphosUri import uriparse_type
from app.dao.AdelphosUri import EAdelphosType
from app.consts import USER_ID
from app.ap_api.AsyncRequest import AsyncGetReq
from fastapi.encoders import jsonable_encoder
import json
import asyncio
import re


from argon2 import PasswordHasher


def validate_local_name(alias):

    if (re.match("[a-z0-9][a-z0-9_-]+[a-z0-9]+", alias, 
                 re.IGNORECASE) is None):
        raise AdelphosException(f"Invalid name {alias}, \
it must begin and end with a letter or a digit.")

    if (len(alias) < 2 or len(alias) > 64):
        raise AdelphosException(f"name length incorrect")


def err_middleware(func):

    async def func_safe(ctx):
        try:
            return await func(ctx)
        except AdelphosException as err:
            return f"Error during command: {str(err)}"
        except Exception as err_ex:
            return f"Server error during command: {str(err_ex)}"

    return func_safe 


@err_middleware
async def alias_create_handler(ctx):

    # first of all let's see if the alias is already present
    alias_complete = get_param_safe(ctx, 'alias')
    password = get_param_safe(ctx, 'password')
    currency = get_param_safe(ctx, 'currency')
    equity = get_param_safe(ctx, 'equity')

    host = ctx.app.config['General']['host']

    alias_uri = uriparse(alias_complete)

    gCon.log(f"alias uri created {alias_uri}")

    # OK, now I can try to create the alias.
    # first of all I get the local currency

    # as I know that the currency is a currency I can add the type.
    currency_uri = uriparse_type(currency, EAdelphosType.CURRENCY_TYPE)

    gCon.log(f"currency uri is {currency_uri}")

    return f"Created alias {alias_uri.name} successfully.\
Your global identifier in adelphos fediverse is {alias_uri}"


    alias_family_splits = alias_complete.split(".")
    if (len(alias_family_splits) == 1):
        raise AdelphosException(
f"I need the alias written in the form alias.family, with a '.' \
in the middle")

    if (len(alias_family_splits) > 1):
        raise AdelphosException(
f"Too many dots in the alias! {alias_complete}, Only one is allowed")

    (alias, family_name) = alias_family_splits

    # the family MUST NOT already exist, we cannot create two families in
    # the same instance with the same name.
    family_raw = FamilyDao.get_local_family(ctx, family_name)

    if (family_raw is not None):
        raise AdelphosException(
f"family {family_raw.name} is already existing in this instance")

    # this must not fail, unless there is an exception.
    currency_raw = CurrencyDao.get_or_create_currency(ctx, currency)

    # this function question the database using the local alias, so
    # it means that the instance is local.
    #ctx.alias = AliasDao.exists_local_alias(ctx, alias)

    #if (ctx.alias is not None):
    #    raise AdelphosException(
#f"alias: {alias} already existing in this instance")

    validate_local_name(alias)

    validate_local_name(family_name)

    # OK, now I have to create the Family and Alias objects.

    
    
    # of course the instance for these objects will be zero, it is the
    # local instance.l

    # first the family object.

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
    wsctx.actor = await ActorDto.get_or_discover_actor(wsctx, "lino_ferre",
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


