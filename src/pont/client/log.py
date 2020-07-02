import logging

class LogManager:
	def __init__(self, level=logging.DEBUG, log_path=None, client=None):
		self._client = client
		self._level = level
		self._format = '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s'
		self._datefmt = '%H:%M:%S'
		self._formatter = logging.Formatter(self._format)
		self._formatter.datefmt = self._datefmt

		self.log_path = log_path
		self.loggers = {}
		self.handlers = []
		if log_path is not None:
			self.add_file_handler(log_path)

	def add_file_handler(self, filename: str):
		handler = logging.FileHandler(filename=filename, mode='a')
		handler.setFormatter(self._formatter)

		self.handlers.append(handler)
		for _, logger in self.loggers.items():
			if handler not in logger.handlers:
				logger.addHandler(handler)

	@property
	def level(self):
		return self._level

	@level.setter
	def level(self, level):
		self._level = level
		for _, logger in self.loggers.items():
			logger.setLevel(level)

	@property
	def format(self):
		return self._format

	@format.setter
	def format(self, format):
		self._format = format
		self._formatter = logging.Formatter(self._format)
		self._formatter.datefmt = self._datefmt
		for _, logger in self.loggers.items():
			# Set our own formatting in all of the handlers.
			for handler in logger.handlers:
				handler.setFormatter(self._formatter)

	def __getitem__(self, name) -> logging.Logger:
		return self.get_logger(name)

	def get_logger(self, name) -> logging.Logger:
		if name not in self.loggers:
			logger = logging.getLogger(name)
			logger.setLevel(self._level)

			# Add our custom handlers.
			for handler in self.handlers:
				if handler not in logger.handlers:
					logger.addHandler(handler)

			# Set our own formatting in all of the handlers.
			for handler in logger.handlers:
				handler.setFormatter(self._formatter)

			self.loggers[name] = logger

		return self.loggers[name]

mgr = LogManager()

