import logging
import os
import traceback


class Singleton(type):
	_instances = {}

	def __call__(cls, *args, **kwargs):
		if cls not in cls._instances:
			cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
		return cls._instances[cls]


def configure_logging():
	log_formatter = logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")
	root_logger = logging.getLogger()
	root_logger.setLevel(logging.DEBUG)

	console_handler = logging.StreamHandler()
	console_handler.setFormatter(log_formatter)
	console_handler.setLevel(logging.DEBUG)
	root_logger.addHandler(console_handler)


def format_exception(exception):
	return os.linesep.join(traceback.format_exception_only(type(exception), exception))

