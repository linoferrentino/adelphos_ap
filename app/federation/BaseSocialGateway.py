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


from app.federation.SocialGateway import SocialGateway
from abc import abstractmethod, ABC
from app.logging import gCon
from starlette.responses import Response
from starlette.exceptions import HTTPException
from app.sdc.Dependencies import Dependencies


class BaseSocialGateway(SocialGateway):

    def __init__(self, vhost):
        super().__init__(vhost)


    async def in_inbox(self, user, request):

        headers = request.headers
        gCon.log(f"here are the headers {headers}")
        gCon.log(f"here is the url {request.url} type {type(request.url)}")
        gCon.log(f"here is the client {request.client} type {type(request.client)}")

        body = await request.body()
        body_str = body.decode()
        #gCon.log(f"the body string is ---{body_str}---")
        body_ob = await request.json()

        actor_str = body_ob.get('actor')
        if actor_str is None:
            raise HTTPException(401, "Malformed request, no actor")

        #object_body = body_ob.get('object')
        #if object_body is None:
        #    gCon.log("Malformed json, no body")
        #    return Response(status_code=401)

        #content = object_body.get('content')
        #if (content is None):
        #    gCon.log(f"No content in object {object_body}")
        #    return Response(status_code=401)

        #clean_content = re.sub('<[^<]+?>', '', content) 

        #gCon.log(f"[green]Message from {actor_str}[/green]")
        #gCon.log(f"For: url {request.url}")
        #gCon.log(f"Message: [yellow]{clean_content}[/yellow]")

        (actor_from, actor_to, content) = await self._parse_message(user,
                          request, actor_str, body_str, body_ob)

        social = self.vhost.get_dep(Dependencies.SOCIAL)
        await social.incoming_message(user, content)
        return Response(status_code=202)


    @abstractmethod
    async def _parse_message(self, user, request, actor_str, body_str, body_ob):
        pass


