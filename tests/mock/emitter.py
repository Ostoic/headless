import collections
from wlink.log import logger

from pont.utility.emitter import BaseEmitter

def GenericMemoryEmitter(emitter_type):
	class MemoryEmitter(emitter_type):
		Memory = collections.namedtuple('Memory', ['args', 'kwargs'])
		def __init__(self, emitter=None, nursery=None, scope=None):
			super().__init__(emitter=emitter, nursery=nursery, scope=scope)
			self.memory = {}

		def emit(self, event, *args, **kwargs):
			logger.log('EVENTS', f'{event=}, {kwargs}')
			super().emit(event, *args, **kwargs)
			if event in self.memory.keys():
				self.memory[event].append(MemoryEmitter.Memory(args=args, kwargs=kwargs))
			else:
				self.memory[event] = [MemoryEmitter.Memory(args=args, kwargs=kwargs)]
	return MemoryEmitter

MemoryEmitter = GenericMemoryEmitter(BaseEmitter)