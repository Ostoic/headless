import inspect
import trio

from ..client.log import mgr
log = mgr.get_logger(__name__)

class BaseEmitter:
	def __init__(self, emitter, scope = None):
		self._emitter = emitter
		self._scope = scope
		self._events = {}

	def _append_event(self, event, fn):
		if event not in self._events:
			self._events[event] = [fn]
		else:
			self._events[event].append(fn)

	def emit(self, event, *args, **kwargs):
		log.debug(f'[{type(self).__name__}.emit]: emitted {event=}, {kwargs}')
		self._emitter.emit(event, *args, **kwargs)

	def once(self, event, fn = None):
		def _on(fn):
			target_fn = fn
			async def fn_async(*args, **kwargs):
				await trio.lowlevel.checkpoint()
				return fn(*args, **kwargs)

			log.debug(f'[{type(self).__name__}.once]: installed {event=} {fn=}')
			if not inspect.iscoroutinefunction(fn):
				target_fn = fn_async

			return self._emitter.once(event, target_fn)

		if fn is None:
			return _on
		else:
			return _on(fn)

	def on(self, event, fn = None):
		def _on(fn):
			target_fn = fn
			async def fn_async(*args, **kwargs):
				await trio.lowlevel.checkpoint()
				return fn(*args, **kwargs)

			log.debug(f'[{type(self).__name__}.on]: installed {event=} {fn=}')
			if not inspect.iscoroutinefunction(fn):
				target_fn = fn_async

			self._append_event(event, target_fn)
			return self._emitter.on(event, target_fn)

		if fn is None:
			return _on
		else:
			return _on(fn)

class AsyncScopedEmitter(BaseEmitter):
	async def aclose(self):
		log.debug(f'{type(self).__name__} aclose')
		for event, fn_list in self._events.items():
			await trio.lowlevel.checkpoint()
			for fn in fn_list:
				if fn in self._emitter.listeners(event):
					self._emitter.remove_listener(event, fn)

	async def __aenter__(self):
		return self

	async def __aexit__(self, exc_type, exc_val, exc_tb):
		await self.aclose()

class ScopedEmitter(BaseEmitter):
	def close(self):
		log.debug(f'{type(self).__name__} close')
		for event, fn_list in self._events.items():
			for fn in fn_list:
				if fn in self._emitter.listeners(event):
					self._emitter.remove_listener(event, fn)

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		self.close()
