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


from app.cli.CliProvider import CliProvider


class CliHandlerStub(CliProvider):

    async def serve_forever(self, websocket):
        await websocket.accept()
        text = await websocket.receive_text()
        await websocket.send_text(f"Hello world, {text}!")
        await websocket.close()


    def start_sync(self):
        pass


    def stop_sync(self):
        pass
    
