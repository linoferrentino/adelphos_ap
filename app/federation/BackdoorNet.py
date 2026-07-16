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


from app.sdc.Dependency import Dependency
from app.federation.BackdoorRouter import BackdoorRouter
from starlette.routing import Route
import app.consts as CNST
from app.logging import gCon
from starlette.responses import Response
from starlette.responses import JSONResponse
import json
from app.cli.CliParser import CliParser
from app.sdc.Dependencies import Dependencies


class BackdoorNet(BackdoorRouter):
    

    def __init__(self, kernel):
        super().__init__(kernel)


    async def _backdoor_post(self, request):
        body = await request.body()
        gCon.log(f"I will parse {body}")
        body_ob = json.loads(body)
        cliparser = CliParser(body_ob['msg'])
        gCon.log(f"backdoor! cmd {cliparser.cmd}")

        match cliparser.cmd:
            case 'discover_uri':
                uri = cliparser.get_param_safe('uri')
                transport = self.kernel.get_dep(Dependencies.TRANSPORT)
                answer = await transport.get_json(uri)
                return Response(status_code=202, content = answer)
            case _:
                return Response(status_code=405)


    def get_backdoor_routes(self):
        routes = [
                Route(CNST.BACKDOOR_ROUTE,
                      endpoint = self._backdoor_post, methods=['POST']),
                 ]
        return routes

