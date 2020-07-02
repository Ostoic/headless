import construct

from pont.utility.construct import GuidConstruct, PackEnum
from .bank import GuildBank
from .member import MemberStatus
from ..entities.player import Gender, CombatClass
from ..guid import Guid

GuildRankData = construct.ByteSwapped(construct.Struct(
	'flags' / construct.Int,
	'withdraw_gold_limit' / construct.Int,
	'tab_flags' / construct.Array(GuildBank.max_tabs,
		construct.Sequence(construct.Int, construct.Int)
	),
))

RosterMemberData = construct.Struct(
	'guid' / construct.ByteSwapped(GuidConstruct(Guid)),
	'status' / PackEnum(MemberStatus),
	'name' / construct.CString('ascii'),
	'rank_id' / construct.ByteSwapped(construct.Int),
	'level' / construct.Byte,
	'class_id' / PackEnum(CombatClass),
	'gender' / PackEnum(Gender),
	'area_id' / construct.ByteSwapped(construct.Int),
	'last_save' / construct.IfThenElse(construct.this.status == MemberStatus.offline, construct.Float32l, construct.Pass),
	'note' / construct.CString('ascii'),
	'officer_note' / construct.CString('ascii'),
)

class GuildRoster:
	pass