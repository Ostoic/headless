import trio
from trio_socks import socks5
from typing import Optional, Tuple

from . import AuthState
from .errors import AuthError
from pont_client.client.auth.net.protocol import AuthProtocol
from .. import log
from ... import cryptography

log = log.get_logger(__name__)

class AuthSession:
	def __init__(self, nursery, emitter, proxy: Optional[Tuple[str, int]]=None):
		self.proxy = proxy
		self.protocol: Optional[AuthProtocol] = None
		self._nursery = nursery
		self._emitter = emitter
		self._stream: Optional[trio.abc.HalfCloseableStream] = None
		self._srp: Optional[cryptography.srp.WowSrpClient] = None
		self.__session_key = None
		self._state = AuthState.not_connected

	@property
	def state(self):
		return self._state

	async def aclose(self):
		if self._stream is not None:
			await self._stream.aclose()
			self._stream = None

		self._state = AuthState.not_connected

	async def connect(self, address=None, proxy=None, stream=None):
		if stream is None:
			if self.proxy is not None or proxy is not None:
				self._stream = socks5.Socks5Stream(destination=address, proxy=proxy or self.proxy)
				await self._stream.negotiate()

			else:
				self._stream = await trio.open_tcp_stream(*address)
		else:
			self._stream = stream

		self.protocol = AuthProtocol(stream=self._stream)
		# await self.protocol.spawn_receiver(nursery=self._nursery, emitter=self._emitter)
		self._state = AuthState.connected

	async def authenticate(self, username, password, debug=None):
		self._state = AuthState.logging_in
		await self.protocol.send_challenge_request(username=username)

		challenge_response = await self.protocol.receive_challenge_response()
		self._srp = cryptography.srp.WowSrpClient(username=username, password=password,
		    prime=challenge_response.prime,
			generator=challenge_response.generator,
		    client_private=debug['client_private']
		)

		client_public, session_proof = self._srp.process(challenge_response.server_public, challenge_response.salt)
		self.__session_key = self._srp.session_key

		await self.protocol.send_proof_request(client_public=client_public, session_proof=session_proof)
		proof_response = await self.protocol.receive_proof_response()
		print(f'{proof_response.session_proof_hash=} vs {self._srp.session_proof_hash:=}')
		if proof_response.session_proof_hash != self._srp.session_proof_hash:
			self._state = AuthState.not_connected
			raise AuthError('Invalid username or password')

		self._state = AuthState.logged_in

	async def realmlist(self):
		await self.protocol.send_realmlist_request()
		result = await self.protocol.receive_realmlist_response()
		self._state = AuthState.realmlist_ready
		return result
