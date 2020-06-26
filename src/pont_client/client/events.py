import uuid
from enum import Enum

class AuthEvent(Enum):
	# Basic connection events
	connected = uuid.uuid4()
	data_received = uuid.uuid4()

	disconnected = uuid.uuid4()

	realmlist_ready = uuid.uuid4()

	#
	logging_in = uuid.uuid4()
	invalid_login = uuid.uuid4()
	login_success = uuid.uuid4()

auth = AuthEvent

class WorldEvent(Enum):
	# Basic connection events
	connected = uuid.uuid4()
	data_received = uuid.uuid4()

	# Connection error events
	disconnected = uuid.uuid4()

	received_auth_challenge = uuid.uuid4()
	received_auth_response = uuid.uuid4()
	received_name_query_response = uuid.uuid4()
	received_char_enum = uuid.uuid4()

	CMSG_PING_sent = uuid.uuid4()
	CMSG_KEEP_ALIVE_sent = uuid.uuid4()

world = WorldEvent

class ConsoleEvent(Enum):
	data_received = uuid.uuid4()

console = ConsoleEvent

class ConfigEvent(Enum):
	relogger_changed = uuid.uuid4()
	username_changed = uuid.uuid4()
	password_changed = uuid.uuid4()

	auth_server_address_changed = uuid.uuid4()
	character_name_changed = uuid.uuid4()
	realm_name_changed = uuid.uuid4()

config = ConfigEvent