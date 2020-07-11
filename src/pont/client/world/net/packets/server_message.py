from enum import Enum

import construct

from pont.utility.construct import PackEnum
from .constants import Opcode
from .headers import ServerHeader


class ServerMessageType(Enum):
	shutdown_time = 1
	restart_time = 2
	custom = 3
	shutdown_cancelled = 4
	restart_cancelled = 5

SMSG_SERVER_MESSAGE = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_SERVER_MESSAGE, 4),
	'type' / PackEnum(ServerMessageType),
	'text' / construct.CString('ascii')
)
