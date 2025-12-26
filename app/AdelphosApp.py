# the main class of adelphos. This defines the application.


from fastapi import FastAPI

# I create here the main application object.

class AdelphosApp(FastAPI):

    def __init__(self, instance: str, **kwargs):
        super().__init__(**kwargs)
        self.instance = instance

