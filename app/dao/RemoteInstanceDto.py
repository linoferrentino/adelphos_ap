# this is the DTO of the remote instance, used when two
# adelphos want to connect


from dataclasses import dataclass
from app.logging import gCon

table_name = "remote_instance"

@dataclass
class RemoteInstanceDto:

    remote_instance_id: int = 0

    hostname: str = None
    endpoint: str = None
    inbox: str = None
    public_key: str = None

    date_created: str = None


    @staticmethod
    def get_from_hostname(ctx, hostname):

        global table_name

        fields_to_ask = ('remote_instance_id', 
                         'hostname', 'endpoint', 
                         'inbox', 'public_key', 'date_created')
        field_to_seek = 'hostname'
        value_to_seek = hostname 

        dto = ctx.app.dao.get_dto(table_name, fields_to_ask, field_to_seek, 
                            value_to_seek, RemoteInstanceDto)
        return dto


    def store(self, ctx):

        global table_name

        fields_stored = {
                         'hostname': self.hostname,
                         'endpoint': self.endpoint,
                         'inbox': self.inbox,
                         'public_key': self.public_key,
                         }

        new_id = ctx.app.dao.insert_dto(ctx, table_name, fields_stored)

        gCon.log(f"Created new remote_instance with id {new_id}")

        self.remote_instance_id = new_id



