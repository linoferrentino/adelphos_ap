# this is the dispatcher that understands the Adelphos' API.

# this dispatcher answers to local commands only: remote commands from
# other adelphos instances are dispatched in the remote dispatcher.

from .RequestCtx import RequestCtx
from app.logging import gCon
from app.api.OutgressGateway import post_response
from app.api.OutgressGateway import post_daemon_req
from app.ap_api.daemon_qa import daemon_remote_cmd
from app.ap_api.daemon_qa import daemon_a
from app.ap_api.daemon_qa import daemon_q_handler
from app.consts import USER_ID
from app.api.AdelphosException import AdelphosException
from app.dao.AliasDto import AliasDto
#from app.dao.RemoteInstanceDto import RemoteInstanceDto
from app.dao.CachedActorDto import CachedActorDto
from app.consts import USER_ID
from app.ap_api.AsyncRequest import AsyncGetReq
from fastapi.encoders import jsonable_encoder
import json
import asyncio


from argon2 import PasswordHasher

def get_param_safe(ctx, param):
    par_value = ctx.cmd_dict.get(param)
    
    if (par_value is not None):
        return par_value

    raise AdelphosException(f"Required parameter {param} not found")


async def alias_create_handler(ctx):

    # first of all let's see if the alias is already present
    alias = get_param_safe(ctx, 'alias')

    ctx.alias = AliasDto.get_from_alias(ctx, alias)

    if (ctx.alias is not None):
        raise AdelphosException(f"{alias} already existing, cannot insert")

    # OK! Now I can create a new Alias
    ctx.alias = AliasDto()

    ctx.alias.alias = alias

    #clear_pwd = get_param_safe(ctx, 'pwd')

    #ph = PasswordHasher()
    
    #password_hashed = ph.hash(clear_pwd)

    #ctx.alias.password = password_hashed

    ctx.alias.actor_fk = ctx.actor.actor_id

    # OK, let't try to add it to the database
    ctx.alias.store(ctx)

    host = ctx.app.config['General']['host']

    return f"Created alias {alias} successfully.\
Your nick in adelphos is ${alias}@{host}"


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

    # check alias syntax, for now I assume it is OK
    if (alias_to[0] != '$'):
        raise AdelphosException(f"Invalid alias <{alias_to}>")

    # remove the dollar.
    alias_to = alias_to[1:]

    return f"create trust line to {alias_to} OK"


async def create_remote_daemon(ctx, rem_instance):

    daemon_query = f"https://{rem_instance}/.well-known/webfinger?\
resource=acct:{USER_ID}@{rem_instance}"

    daemon_res = AsyncGetReq(daemon_query)
    await ctx.app.async_req_wait(daemon_res)

    if (daemon_res.status_code != 200):
        raise AdelphosException(
            f"remote daemon not responding {rem_instance}")

    daemon_ob = json.loads(daemon_res.text)

    subject = daemon_ob['subject']
    if ( subject != f"acct:{USER_ID}@{rem_instance}"):
        raise AdelphosException(f"got {subject} instead!")

    ctx.daemon = CachedActorDto()
    ctx.daemon.hostname = rem_instance
    ctx.daemon.actor_uri = daemon_ob['links'][0]['href']
    
    # Now we do the request for the actor
    daemon_actor = AsyncGetReq(ctx.daemon.actor_uri)
    await ctx.app.async_req_wait(daemon_actor)

    if (daemon_actor.status_code != 200):
        raise AdelphosException(
            f"remote daemon misconfigured {ctx.daemon.endpoint}")

    daemon_ob = json.loads(daemon_actor.text)

    # OK, we can now take the inbox and the public key.
    ctx.daemon.inbox_uri = daemon_ob['inbox']
    ctx.daemon.public_key = daemon_ob['publicKey']['publicKeyPem']
    ctx.daemon.preferred_username = USER_ID

    ctx.daemon.store(ctx)


async def rem_echo_handler(ctx):
    rem_instance = get_param_safe(ctx, "remote-instance")
    msg = get_param_safe(ctx, "msg")

    gCon.log(f"I have to do an echo to @{USER_ID}@{rem_instance}")

    # I have to query the dao to get the remote, in this case (only in this
    # case) the hostname is sufficient to get the actor, because the
    # preferred username is fixed to `daemon'
    ctx.daemon = CachedActorDto.get_from_hostname(ctx, rem_instance)

    if (ctx.daemon is None):
        await create_remote_daemon(ctx, rem_instance)

    # Now I have the daemon.
    gCon.log(f"remote daemon {ctx.daemon.actor_uri} OK")

    # OK, I now have the message to the remote instance
    rcmd = {
            'cmd' : 'echo',
            'msg' : msg
            }
    ctx.rcmd = rcmd

    await daemon_remote_cmd(ctx)


async def daemon_a_handler(ctx):

    msg = get_param_safe(ctx, "msg")
    local_id = get_param_safe(ctx, "api_id")
    gCon.log(f"got msg {msg} for api {local_id}")

    # I put it into the other context.

    global async_contexts
    async_ctx = async_contexts.pop(int(local_id), None)
    if (async_ctx is None):
        gCon.log(f"What? no context {async_contexts}")
        return

    async_ctx.answer_txt = msg
    asyncio.create_task(daemon_a(async_ctx))
    # my answer is None
    ctx.answer_txt = None


# I have here the command parsers.
cmd_handlers = {
        "alias_create": alias_create_handler,
        "dump_db": dump_db,
        "tl_create": tl_create_handler,
        "recho": rem_echo_handler,
        "daemon_q": daemon_q_handler, 
        "daemon_a": daemon_a_handler, 
}


def make_cmd_params(ctx):
    ctx.cmd_dict = {}
    while (len(ctx.cmd_splits) > 1):
        val = ctx.cmd_splits.pop()
        key = ctx.cmd_splits.pop()
        ctx.cmd_dict[key] = val


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


async def dispatch_request(ctx):
    gCon.rule("--- dispatch request ---")
    gCon.log(f"The message is {ctx.clean_content}")

    # I will have to parse it 
    try:

        await cmd_parse(ctx)

        # I might be in a async context, so I wait for the response.
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


