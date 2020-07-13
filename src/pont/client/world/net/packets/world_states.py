import construct

from ..opcode import Opcode
from .headers import ServerHeader

SMSG_INIT_WORLD_STATES = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_INIT_WORLD_STATES, 14),
	'map_id' / construct.Int32ul,
	'zone_id' / construct.Int32ul,
	'area_id' / construct.Int32ul,
	'world_states' / construct.PrefixedArray(construct.Int16ul, construct.Sequence(construct.Int32ul, construct.Int32ul)),
)
