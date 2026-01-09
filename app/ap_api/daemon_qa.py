# this is the module that implements a remote api
# using Activity Pub between two adelphos instances.

# the API is asynchronous and it is based on an increasing counter to
# divide the queries from other instances.

from app.api.OutgressGateway import post_daemon_req
from app.api.params import get_param_safe
from app.consts import USER_ID
import asyncio
from app.logging import gCon
import base64
import json


# this is the sequence to hold the requests, we have only one thread,
# so it is safe to share.
remote_api_id = 0

# this is the dictionary for the async contexts.
async_contexts = {}


# this is called with the async context defined earlier
async def daemon_a(ctx):
    gCon.log(f"will notify the condition!")
    async with ctx.async_cond:
         ctx.async_cond.notify()


# this API is asynchronous.
async def daemon_query_task(ctx):
    gCon.log(f"I have to send {ctx.query_txt}!")

    await post_daemon_req(ctx)

    gCon.log(f"OK, Now I wait for the end")

    ctx.answer_json = None

    # OK, I have created a new question and I wait
    while ctx.answer_json is None:
        async with ctx.async_cond:
            await ctx.async_cond.wait()

    # Now I have the response, if it is OK I can return it, otherwise I
    # raise a local exception which will be notified in the local async
    # context.
    if (ctx.answer_json['res'] == 0):
        ctx.answer_txt = ctx.answer_json['msg']
        gCon.log(f"finished with answer {ctx.answer_txt}")
    else:
        gCon.log("error remote, I will raise an exception")
        raise AdelphosException(f"remote error {ctx.answer_json}")


# a synchronous function to decode the payload and return the dictionary.
def extract_payload(ctx):
    remote_payload_b64str = get_param_safe(ctx, "payload")
    remote_payload_b = base64.b64decode(remote_payload_b64str.encode())
    remote_payload_str = remote_payload_b.decode()
    remote_json = json.loads(remote_payload_str)
    return remote_json


async def daemon_a_handler(ctx):

    #ctx.rem_id = get_param_safe(ctx, "api_id")

    # I have to extract the payload...
    gCon.log("................ extract payload")
    remote_json = extract_payload(ctx)

    #msg = get_param_safe(ctx, "msg")
    local_id = get_param_safe(ctx, "api_id")
    
    gCon.log(f"got msg {remote_json} for api {local_id}")

    # I put it into the other context.

    global async_contexts
    async_ctx = async_contexts.pop(int(local_id), None)
    if (async_ctx is None):
        gCon.log(f"What? no context {async_contexts}")
        return

    async_ctx.answer_json = remote_json
    asyncio.create_task(daemon_a(async_ctx))
    # my answer is None
    ctx.answer_txt = None



# this is the entry point for the remote API
async def daemon_q_handler(ctx):
    # OK, now I get the message.
    # msg = get_param_safe(ctx, "msg")
    ctx.rem_id = get_param_safe(ctx, "api_id")

    # I have to get the payload, and decode it.

    remote_json = extract_payload(ctx)

    gCon.log(f"I will marshall the command {remote_json['cmd']}")

    # Now I simulate only the echo command
    # here an exception local will be translated to an error code.
    ctx.daemon_post_ob = {
            "res" : 0,
            "msg" : f"I have received: {remote_json['msg']}"
            }

    # and get the command, now I have to dispatch the command

    # I build the response
    #response = f"@{USER_ID} daemon_a api_id {rem_id} msg parsed_{msg}_good"

    #gCon.log(f"Got {msg} I will respond with {response}")

    await daemon_remote_answer(ctx)

    # the message is not sent in the normal way, but with the
    # b64 payload.
    return None 


# this function builds the remote string to send to a daemon, depending
# if this is a query or an answer.
def build_remote_string(ctx):
    is_answer = hasattr(ctx, "rem_id")

    if (is_answer == True):
        rem_id = ctx.rem_id
        daemon_cmd = "daemon_a"
    else:
        global remote_api_id
        remote_api_id += 1
        rem_id = remote_api_id
        daemon_cmd = "daemon_q"

    rcmd_str = json.dumps(ctx.daemon_post_ob)
    remote_payload = base64.b64encode(rcmd_str.encode())
    remote_payload_str = remote_payload.decode()

    ctx.query_txt = f"@{USER_ID} {daemon_cmd} api_id {rem_id} \
payload {remote_payload_str}"

    gCon.log(f"sending {ctx.query_txt} to daemon")

    return rem_id


    # Now I will post it, if it is an answer I only post the response,
    # otherwise I have to create an async context and wait for it.



# this function will create the payload with a new id and post it
async def daemon_remote_query(ctx):
    rem_id = build_remote_string(ctx)

    # Now I have to create an async context for the query
    ctx.async_cond = asyncio.Condition()  
    ctx.async_ctx = asyncio.create_task(daemon_query_task(ctx))

    global async_contexts

    new_async_id = rem_id

    async_contexts[int(new_async_id)] = ctx
    gCon.log(f"Created async context for id {new_async_id}")


async def daemon_remote_answer(ctx):
    build_remote_string(ctx)

    # for now I simply pretend that the daemon is an actor, which in some
    # way it is true
    if (hasattr(ctx, 'daemon') == False):
        gCon.log(f"No daemon, will post to {ctx.actor.actor_uri}")
        ctx.daemon = ctx.actor
    else:
        gCon.log(f"There is daemon, will post to {ctx.daemon.actor_uri}")
        gCon.log(f"There is daemon, actor is {ctx.actor.actor_uri}")

    # simply do the post, without waiting
    await post_daemon_req(ctx)



# this function marshals the command into a json object which the other
# party will unmarshall in the daemon_q_handler
async def daemon_remote_cmd(ctx):

    rcmd_str = json.dumps(ctx.daemon_post_ob)
    remote_payload = base64.b64encode(rcmd_str.encode())
    remote_payload_str = remote_payload.decode()

    gCon.log(f"sending {remote_payload_str}")
 
    # the remote command is encapsulated into a daemon query
    ctx.query_txt = f"@{USER_ID} daemon_q api_id {remote_api_id} \
payload {remote_payload_str}"

    gCon.log(f"I will send {ctx.query_txt}")
   
    ctx.async_ctx = asyncio.create_task(daemon_query_task(ctx))

    global async_contexts

    new_async_id = remote_api_id
    ctx.async_cond = asyncio.Condition()  

    async_contexts[int(new_async_id)] = ctx

    gCon.log(f"Created async context for id {new_async_id}")
