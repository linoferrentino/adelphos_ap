# this is the module that implements a remote api
# using Activity Pub between two adelphos instances.

from app.api.OutgressGateway import post_daemon_req
import asyncio
from app.logging import gCon


# this is called with the async context defined earlier
async def daemon_a(ctx):
    gCon.log(f"will notify the condition!")
    async with ctx.async_cond:
         ctx.async_cond.notify()


# this API is asynchronous.
async def daemon_qa(ctx):
    gCon.log(f"I have to send {ctx.query_txt}!")

    post_daemon_req(ctx)

    gCon.log(f"OK, Now I wait for the end")

    ctx.answer_txt = None

    # OK, I have created a new question and I wait
    while ctx.answer_txt is not None:
        async with ctx.async_cond:
            await ctx.async_cond.wait()

    #await asyncio.sleep(3)
    # OK, now I have to yield until some condition happens.

    # Now I have waited, the other "thread" has given the answer

    gCon.log(f"finished with answer {ctx.answer_txt}")
