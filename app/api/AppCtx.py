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
#
# this is the main context used by all the clients,
# either called from the web socket or by the client

from app.api.Gateway import Gateway
from app.api.AliasApi import AliasApi
from app.api.TrustLineApi import TrustLineApi
import shlex
from abc import ABC
from app.api.AdelphosException import AdelphosException
from abc import abstractmethod
from app.logging import gCon
import asyncio
import traceback

# The application context holds the transient data to fulfill a request
# or an interactive session with a client.



