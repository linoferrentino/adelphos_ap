# this is the module that implements a remote api
# using Activity Pub between two adelphos instances.

# the API is asynchronous and it is based on an increasing counter to
# divide the queries from other instances.

from app.api.OutgressGateway import post_daemon_req
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

    ctx.answer_txt = None

    # OK, I have created a new question and I wait
    while ctx.answer_txt is None:
        async with ctx.async_cond:
            await ctx.async_cond.wait()

    gCon.log(f"finished with answer {ctx.answer_txt}")


# this is the entry point for the remote API
async def daemon_q_handler(ctx):
    # OK, now I get the message.
    #msg = get_param_safe(ctx, "msg")
    #rem_id = get_param_safe(ctx, "api_id")

    # I have to get the payload

    # and get the command, now I have to dispatch the command

    # I build the response
    response = f"@{USER_ID} daemon_a api_id {rem_id} msg parsed_{msg}_good"

    gCon.log(f"Got {msg} I will respond with {response}")

    return response


async def daemon_remote_cmd(ctx):

    global remote_api_id
    remote_api_id += 1

    rcmd_str = json.dumps(ctx.rcmd)
    remote_payload = base64.b64encode(ctx.json_cmd.encode())
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
