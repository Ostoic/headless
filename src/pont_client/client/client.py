from contextlib import asynccontextmanager, AsyncExitStack
from typing import Tuple, Optional

import trio
import pyee
from enum import Enum

from . import log, Config
from .auth import AuthSession, AuthState
from .world.session import WorldSession
from ..utility import AsyncScopedEmitter, enum

log = log.get_logger(__name__)

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
	def __init__(self, nursery, proxy=None):
		super().__init__(emitter=None)
		self._reset(proxy)
		self.config = Config(
			relogger=False,
			emitter=self
		)

		self.nursery = nursery
		self._emitter = pyee.TrioEventEmitter(nursery=self.nursery)
		self.auth = AuthSession(nursery=self.nursery, emitter=self, proxy=self._proxy)
		self.world = WorldSession(nursery=self.nursery, emitter=self, proxy=self._proxy)

	def _reset(self, proxy=None):
		self._proxy = proxy
		self._state = ClientState.not_connected
		self.auth = None
		self.world = None
		self._session_key = None
		self.framerate = 60

	async def aclose(self):
		if self.auth is not None:
			await self.auth.aclose()

		if self.world is not None:
			await self.world.aclose()

		await trio.lowlevel.checkpoint()

		self._reset()
		await super().aclose()

	async def login(self, username: str, password: str, address: Tuple[str, int], proxy: Optional[Tuple[str, int]]=None):
		await self.auth.connect(address, proxy=proxy)
		await self.auth.authenticate(username=username, password=password)

	@property
	def state(self) -> ClientState:
		return self._state

	def is_at_character_select(self):
		return self.state == ClientState.character_select

	def is_loading(self):
		return self.state == ClientState.loading_world

	def is_logging_in(self):
		return self.state == ClientState.logging_in

	def is_logged_in(self):
		return self.state >= ClientState.logged_in

	def is_ingame(self):
		return self.state == ClientState.in_game

	def is_connected(self):
		return self.state != ClientState.not_connected

@asynccontextmanager
async def open_client(proxy=None):
	'''
	Creates a client and
	:param proxy: address of the proxy server to use
	:return: Client
	'''
	async with trio.open_nursery() as nursery:
		client = Client(nursery, proxy=proxy)
		try:
			yield client
			nursery.cancel_scope.cancel()
		finally:
			await client.aclose()
