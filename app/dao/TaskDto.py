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

from dataclasses import dataclass
from app.dao.FdObjectDto import FdObjectDto
from enum import IntEnum


# the duty is something that must be done, the duty in adelphos
# is a part of a transaction.

# there is a situation, the duty to be done (and that the other part acknowledges)
# and a result situation

# The duty is placed in two aliases, a high level duty is always related to a
# person responsible for that action.

# In level zero, the family, each member of the family has "full powers", except
# for minors. In this case every member of the family could accomplish and
# acknowledge a certain duty

# the duty is not a federated object, it is part of the transient nature of
# the database, duties come and go.


class ETaskType(IntEnum):
    CARRY_OBJECT
    GIVE_MONEY
    GIVE_SERVICE
    GIVE_OBJECT
    TRANSPORT_PERSON


# carry object: use a carrier_line
# give money: use a credit line
# give service: in response to an ad
# give object: in response to an ad
# transport_person: another kind of service: use a transport line



@dataclass
class TaskDto:

    pass


