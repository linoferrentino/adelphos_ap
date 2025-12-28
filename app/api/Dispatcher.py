# this is the dispatcher that understands the Adelphos' API.

from .RequestCtx import RequestCtx
from app.logging import gCon
from app.api.OutgressGateway import post_response


def cmd_parse(ctx):

    # the first string is the @daemon
    cmd_splits = ctx.clean_content.split()

    
    if (cmd_splits[0] != "@daemon"):
        gCon.log("This is not a message for me")
        return

    # the answer needs to be serialized.
    ctx.answer_txt = f"Response for {cmd_splits[1]}"

    post_response(ctx)


async def dispatch_request(ctx):
    gCon.rule("--- dispatch request ---")
    gCon.log(f"The message is {ctx.clean_content}")

    # I will have to parse it 
    cmd_parse(ctx)


