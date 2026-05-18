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



class CliController(ABC):


    def __init__(self):
        self.handlers = dict()


    def add_handler(self, command_str, other_self, handler):
        self.handlers[command_str] = (other_self, handler)


    async def proc_cli(self, parsed_cli):

        # search for the handler for this command.
        handler_tuple = self.handlers.get(parsed_cli.cmd)
        if handler_tuple is None:
            raise AdelphosException(
                    f"Not found command  {self.cmd}",
                    EAdelhposErrno.ECOMMAND_NOT_FOUND)
        msg_out = await handler_tuple[1](handler_tuple[0], parsed_cli)
        return msg_out


