import construct

from pont_client.utility.construct import ConstructEnum
from .constants import Opcode

RealmlistRequest = construct.Struct(
	'opcode' / construct.Default(construct.Const(Opcode.realm_list, ConstructEnum(Opcode)), Opcode.realm_list),
	construct.Padding(4)
)
