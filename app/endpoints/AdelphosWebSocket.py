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

from starlette.endpoints import WebSocketEndpoint 
from app.logging import gCon

class AdelphosWebSocket(WebSocketEndpoint):
    encoding = "text"


    async def on_connect(self, websocket):
        gCon.log("Accept")
        await websocket.accept()


    async def on_receive(self, websocket, data):
        gCon.log("on receive")
        await websocket.send_text(f"Message text was: {data}")


    async def on_disconnect(self, websocket, close_code):
        gCon.log("Disconnect")
