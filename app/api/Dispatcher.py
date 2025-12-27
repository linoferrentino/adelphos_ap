# this is the dispatcher that understands the Adelphos' API.

from .RequestCtx import RequestCtx
from app.logging import gCon

async def dispatch_request(ctx):
    gCon.rule("--- dispatch request ---")

## the dispatcher is called asynchronously.
#class Dispatcher:
#
#    def __init__(self):
#        pass
#
#    # gets the message from the outside, and dispatches it to the right
#    # objects, the processing is done asynchronously
#    def take_message(self, ctx):
#        pass
