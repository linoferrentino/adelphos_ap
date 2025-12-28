
# This is the request context used to store the data during a request.

class RequestCtx:


    def __init__(self, app, request):
        self.app = app
        self.request = request

        self.need_commit = False



