# this is the dispatcher that understands the Adelphos' API.

from .RequestCtx import RequestCtx
from app.logging import gCon
from app.api.OutgressGateway import post_response
from app.api.OutgressGateway import post_daemon_req
from app.ap_api.daemon_qa import daemon_qa
from app.ap_api.daemon_qa import daemon_a
from app.consts import USER_ID
from app.api.AdelphosException import AdelphosException
from app.dao.AliasDto import AliasDto
from app.dao.RemoteInstanceDto import RemoteInstanceDto
import requests
from app.consts import USER_ID
import json
import asyncio


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


def tl_create_handler(ctx):
    alias = get_param_safe(ctx, 'alias')
    trust = get_param_safe(ctx, 'trust')

    # check alias syntax, for now I assume it is OK
    if (alias[0] != '$'):
        raise AdelphosException("Invalid alias")

    # remove the dollar.
    alias = alias[1:]

    return "create alias OK"


def create_remote_daemon(ctx, rem_instance):

    daemon_query = f"https://{rem_instance}/.well-known/webfinger?\
resource=acct:{USER_ID}@{rem_instance}"

    headers_acc = {"Accept" : "application/activity+json"}
    daemon_res = requests.get(daemon_query, headers = headers_acc)

    if (daemon_res.status_code != 200):
        raise AdelphosException(
            f"remote daemon not responding {rem_instance}")

    daemon_ob = json.loads(daemon_res.text)

    subject = daemon_ob['subject']
    if ( subject != f"acct:{USER_ID}@{rem_instance}"):
        raise AdelphosException(f"got {subject} instead!")

    ctx.daemon = RemoteInstanceDto()
    ctx.daemon.hostname = rem_instance
    ctx.daemon.endpoint = daemon_ob['links'][0]['href']
    
    # Now we do the request for the actor
    daemon_actor = requests.get(ctx.daemon.endpoint, headers = headers_acc)

    if (daemon_actor.status_code != 200):
        raise AdelphosException(
            f"remote daemon misconfigured {ctx.daemon.endpoint}")

    daemon_ob = json.loads(daemon_actor.text)

    # OK, we can now take the inbox and the public key.
    ctx.daemon.inbox = daemon_ob['inbox']
    ctx.daemon.public_key = daemon_ob['publicKey']['publicKeyPem']

    ctx.daemon.store(ctx)

# this is the sequence to hold the requests, we have only one thread,
# so it is safe to share.
remote_api_id = 0

# this is the dictionary for the async contexts.
async_contexts = {}


def rem_echo_handler(ctx):
    rem_instance = get_param_safe(ctx, "remote-instance")
    msg = get_param_safe(ctx, "msg")

    gCon.log(f"I have to do an echo to {rem_instance}")

    # I have to query the dao to get the remote
    ctx.daemon = RemoteInstanceDto.get_from_hostname(ctx, rem_instance)

    if (ctx.daemon is None):
        create_remote_daemon(ctx, rem_instance)

    # Now I have the daemon.
    gCon.log(f"remote daemon {ctx.daemon.endpoint} OK")

    # TODO, create an async context object
    global remote_api_id
    remote_api_id += 1

    ctx.query_txt = f"daemon_q api_id {remote_api_id} msg {msg}"
    
    ctx.async_ctx = asyncio.create_task(daemon_qa(ctx))

    global async_contexts

    new_async_id = remote_api_id
    ctx.async_cond = asyncio.Condition()  

    async_contexts[new_async_id] = ctx

    return f"Created async context for id {new_async_id}"


# this is the entry point for the remote API
def daemon_q_handler(ctx):
    # OK, now I get the message.
    msg = get_param_safe(ctx, "msg")
    rem_id = get_param_safe("api_id")


    # I build the response
    response = f"daemon_a api_id {rem_id} msg parsed_{msg}_good"

    gCon.log(f"Got {msg} I will respond with {response}")

    return response 


def daemon_a_handler(ctx):

    msg = get_param_safe(ctx, "msg")
    local_id = get_param_safe("api_id")
    global async_contexts
    gCon.log(f"got msg {msg} for api {api_id}")

    # I put it into the other context.
    async_ctx = async_contexts.get(local_id)
    if (async_ctx is None):
        gCon.log("What? no context")

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

    # I might be in a async context, so I wait for the response.
    if (ctx.async_ctx is not None):
        gCon.log("I have to wait an async context")
        await ctx.async_ctx

    # No async, I can give immediately the response
    if (ctx.answer_txt is not None):
        post_response(ctx)


