from contextlib import asynccontextmanager
from typing import Tuple

import pyee
import trio

from . import log, auth
from .auth import AuthSession, AuthState, Realm
from .config import Config
from .world.character_select import CharacterInfo
from .world.session import WorldSession
from .world.state import WorldState
from ..utility import AsyncScopedEmitter, enum

log = log.mgr.get_logger(__name__)

@asynccontextmanager
async def open_client(auth_server=None, proxy=None):
	'''
	Creates a client and
	:param auth_server: the address of the auth server to connect to.
	:param proxy: address of the proxy server to use.
	:return: an unconnected Client
	'''
	async with trio.open_nursery() as nursery:
		client = Client(nursery, auth_server=auth_server, proxy=proxy)
		try:
			yield client
			nursery.cancel_scope.cancel()
		finally:
			await client.aclose()

class ClientState(enum.ComparableEnum):
	not_connected = 1
	connected = 2
	logging_in = 3
	logged_in = 4
	realmlist = 5
	character_select = 6
	loading_world = 7
	in_game = 8

class Client(AsyncScopedEmitter):
	def __init__(self, nursery, auth_server: Tuple[str, int], proxy=None):
		super().__init__(emitter=None)
		from . import log
		log.mgr.add_file_handler('pont.log')
		self._auth_server = auth_server
		self._proxy = proxy
		self._username = None
		self._reset()
		self.config = Config(
			emitter=self,
			relogger=False,
			# log='./pont.log',
		)

		self.nursery = nursery
		self._emitter = pyee.TrioEventEmitter(nursery=self.nursery)
		self.auth = AuthSession(nursery=self.nursery, emitter=self, proxy=self._proxy)
		self.world = WorldSession(nursery=self.nursery, emitter=self, proxy=self._proxy)

	@property
	def auth_server(self):
		return self._auth_server

	@auth_server.setter
	def auth_server(self, other: Tuple[str, int]):
		if self.auth.state > AuthState.not_connected:
			raise auth.ProtocolError('Already connected to an auth server')

		self._auth_server = other

	def _reset(self):
		self._state = ClientState.not_connected
		self._session_key = None
		self._username = None
		self.auth = None
		self.world = None
		self.framerate = 60

	async def aclose(self):
		if self.auth is not None:
			await self.auth.aclose()

		if self.world is not None:
			await self.world.aclose()

		await trio.lowlevel.checkpoint()

		self._reset()
		await super().aclose()

	async def login(self, username: str, password: str):
		'''
		Connect to the auth server and then authenticate using the given username and password.
		:param username: username to use.
		:param password: password to use.
		:return: None
		'''
		self._username = username
		if self.auth.state < AuthState.connected:
			await self.auth.connect(self._auth_server, proxy=self._proxy)

		await self.auth.authenticate(username=username, password=password)

	async def realms(self):
		if self.auth.state < AuthState.logged_in:
			raise auth.ProtocolError('Must be logged into the auth server')

		return await self.auth.realmlist()

	async def select_realm(self, realm: Realm):
		if self.auth.state < AuthState.logged_in:
			raise auth.ProtocolError('Must at least be logged into the auth server')

		await self.world.connect(realm, proxy=self._proxy)
		await self.world.authenticate(self._username, self.auth.session_key)

	async def characters(self):
		if self.world.state < WorldState.logged_in:
			raise auth.ProtocolError('Must be logged into the world server')
		return await self.world.characters()

	async def enter_world(self, character: CharacterInfo):
		if self.world.state < WorldState.logged_in:
			raise auth.ProtocolError('Must be logged into the world server')
		await self.world.enter_world(character.guid)

	@property
	def state(self) -> ClientState:
		return self._state

	def is_at_character_select(self):
		return self.world.state >= WorldState.logged_in

	def is_loading(self):
		return self.world.state == WorldState.loading

	def is_logging_in(self):
		return self.state == WorldState.logging_in

	def is_logged_in(self):
		return self.auth.state >= AuthState.logged_in

	def is_ingame(self):
		return self.world.state >= WorldState.in_game
