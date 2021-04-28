import inspect
import time

from wlink.log import logger
from wlink.world import Opcode
from wlink.world.packets import SMSG_TIME_SYNC_REQ, SMSG_MESSAGECHAT

from pont import events
from pont.world.chat import ChatMessage

class WorldHandler:
	def __init__(self, emitter, world):
		self._emitter = emitter
		self._world = world
		self._packet_map = {
			Opcode.SMSG_MESSAGECHAT: self.handle_received_chat_message,
			Opcode.SMSG_GM_MESSAGECHAT: self.handle_received_chat_message,
		}

		self._dropcodes = [Opcode.SMSG_COMPRESSED_UPDATE_OBJECT, Opcode.SMSG_UPDATE_OBJECT]
		self._opcode_event_map = {
			Opcode.SMSG_QUERY_TIME_RESPONSE: events.world.received_time_query_response,
			Opcode.SMSG_MAIL_LIST_RESULT: events.world.received_mail_list,
			Opcode.SMSG_RECEIVED_MAIL: events.world.received_new_mail,
			Opcode.SMSG_AUTH_RESPONSE: events.world.received_auth_response,
			Opcode.SMSG_TUTORIAL_FLAGS: events.world.received_tutorial_flags,
			Opcode.SMSG_LOGOUT_CANCEL_ACK: events.world.logout_cancelled,
			Opcode.SMSG_LOGOUT_RESPONSE: events.world.received_logout_response,
			Opcode.SMSG_LOGOUT_COMPLETE: events.world.logged_out,
			Opcode.SMSG_NAME_QUERY_RESPONSE: events.world.received_name_query_response,
			Opcode.SMSG_BIND_POINT_UPDATE: events.world.received_bind_point,
			Opcode.SMSG_GROUP_INVITE: events.world.received_group_invite,
			Opcode.SMSG_GROUP_LIST: events.world.received_group_list,
			Opcode.SMSG_GUILD_INVITE: events.world.received_guild_invite,
			Opcode.SMSG_GUILD_EVENT: events.world.received_guild_event,
			Opcode.SMSG_GUILD_INFO: events.world.received_guild_info,
			Opcode.SMSG_GUILD_ROSTER: events.world.received_guild_roster,
			Opcode.SMSG_GUILD_QUERY_RESPONSE: events.world.received_guild_query_response,
			Opcode.SMSG_DUEL_REQUESTED: events.world.received_duel_request,
			Opcode.SMSG_PONG: events.world.received_pong,
			Opcode.SMSG_WARDEN_DATA: events.world.received_warden_data,
			Opcode.SMSG_LOGIN_VERIFY_WORLD: events.world.entered_world,
			Opcode.SMSG_CHAR_ENUM: events.world.received_char_enum,
			Opcode.SMSG_CHAR_CREATE: events.world.received_character_create,
			Opcode.SMSG_MOTD: events.world.received_motd,
			Opcode.SMSG_NOTIFICATION: events.world.received_notification,
			Opcode.SMSG_SERVER_MESSAGE: events.world.received_server_message,
			Opcode.SMSG_CONTACT_LIST: events.world.received_contact_list,
			Opcode.SMSG_TIME_SYNC_REQ: events.world.received_time_sync_request,

		}

		self._world = world
		self._handler_start_time = time.time()

	def set_handler(self, event, handler):
		self._packet_map[event] = handler

	def default_handle_event_packet(self, packet, event):
		self._emitter.emit(event, packet=packet)
		logger.log('PACKETS', f'{packet=}')

	async def handle(self, packet):
		try:
			logger.log('PACKETS', f'{packet=}')
			self._emitter.emit(events.world.received_packet, packet=packet)
			fn = self._packet_map[packet.header.opcode]

			if fn is None or packet.header.opcode in self._dropcodes:
				logger.log('PACKETS', f'Dropped packet: {packet.header=}')
				return

			if inspect.iscoroutinefunction(fn):
				# noinspection PyUnresolvedReferences, PyArgumentList
				return await fn(packet)
			else:
				# noinspection PyArgumentList
				return fn(packet)

		except KeyError:
			# If there is no specific handler then try the default event packet handler
			try:
				event = self._opcode_event_map[packet.header.opcode]
				self.default_handle_event_packet(packet, event)

			except KeyError:
				logger.log('PACKETS', f'Dropped packet: {packet.header=}')

	async def _handle_chat_message(self, packet):
		message = await ChatMessage.load_message(self._world, packet)
		self._emitter.emit(events.world.received_chat_message, message=message)
		logger.log('PACKETS', f'packet={packet}')

	async def handle_received_chat_message(self, packet: SMSG_MESSAGECHAT):
		self._world.nursery.start_soon(self._handle_chat_message, packet)
