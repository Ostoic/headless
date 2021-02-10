from enum import Enum
from typing import Optional

from pont.client.world.errors import ProtocolError
from pont.client.world.net.opcode import Opcode
from pont.client.world.state import WorldState

class GuildMemberDataType(Enum):
	zone_id = 1
	level = 2

class GuildCommandType(Enum):
	create = 0
	invite = 1
	quit = 3
	roster = 5
	promote = 6
	demote = 7
	remove = 8
	change_leader = 10
	edit_motd = 11
	guild_chat = 13
	founder = 14
	change_rank = 16
	public_note = 19
	view_tab = 21
	move_item = 22
	repair = 25

class GuildCommandError(Enum):
	success = 0
	internal_error = 1
	already_in_guild = 2
	already_in_guild_s = 3
	already_invited_to_guild = 4
	already_invited_to_guild_s = 5
	guild_name_invalid = 6
	guild_name_exists = 7
	error_leader_leave = 8
	error_guild_permissions = 8
	player_not_in_guild = 9
	player_not_in_guild_s = 10
	player_not_found_s = 11
	not_allied = 12
	rank_too_high_s = 13
	rank_too_low_s = 14
	ranks_locked = 17
	rank_in_use = 18
	ignoring_you_s = 19
	unknown1 = 20 # Forces roster update
	withdraw_limit = 25
	not_enough_money = 26
	bank_full = 28
	item_not_found = 29

# noinspection PyTypeChecker
class GuildRankRights(Enum):
	empty = 0x00000040
	guild_chat_listen = empty | 0x00000001
	guild_chat_speak = empty | 0x00000002
	officer_chat_listen = empty | 0x00000004
	officer_chat_speak = empty | 0x00000008
	invite = empty | 0x00000010
	remove = empty | 0x00000020
	promote = empty | 0x00000080
	demote = empty | 0x00000100
	set_motd = empty | 0x00001000
	ep_note = empty | 0x00002000
	view_officer_note = empty | 0x00004000
	edit_officer_note = empty | 0x00008000
	modify_guild_info = empty | 0x00010000
	withdraw_gold_lock = 0x00020000
	withdraw_repair = 0x00040000
	withdraw_gold = 0x00080000
	create_guild_event = 0x00100000
	all = 0x001DF1FF

# TODO: Guild will be a generic interface that has all the privileged and non-privileged functions of a guild.
#   Each privilege is checked before executing the corresponding feature and any access violations are thrown as
#   exceptions.
class Guild:
	max_ranks = 10
	min_ranks = 5

	def __init__(self, world, name: Optional[str]=None):
		self._info = None
		self._world = world
		self._name = name
		self._access_token = None

		if world.state < WorldState.in_game:
			raise ProtocolError(f'Must be in-game to send a chat message; world state is {self._world.state} instead')

	@property
	def name(self):
		if self._info is not None:
			return self._info.name

	@property
	def ranks(self):
		if self._info is not None:
			return self._info.ranks

	# async def ginvite(self, name: str):
	# 	# if not self._access_token.has_authority_to(Actions.guild_invite):
	# 	# 	raise PermissionError(f'{self._access_token} is not authorized to invite guild members')
	# 	self._world.

	async def roster(self):
		await self._world.protocol.send_CMSG_GUILD_ROSTER()
		return await self._world.wait_for_packet(Opcode.SMSG_GUILD_ROSTER)

	# async def _send_query