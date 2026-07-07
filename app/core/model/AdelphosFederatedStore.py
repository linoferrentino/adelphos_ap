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


from app.federation.FederatedStore import FederatedStore
from app.core.model.schema import adelphos_schema_yaml


class AdelphosFederatedStore(FederatedStore):


    def __init__(self, kernel):
        super().__init__(kernel, schema = adelphos_schema_yaml)

