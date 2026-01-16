# this is the main context used by all the clients,
# either called from the web socket or by the client

class AppCtx:


    def __init__(self, app):
        self.app = app
        # at first there is not a login.
        self.token = None



# the class that holds the data relative to a client
# this holds a session state for the socket.
class WebSocketContext(AppCtx):

    def __init__(self, app, websocket):
        super().__init__(app)
        self.actor = None
        self.websocket = websocket


