import logging

import cherrypy

from yourss.stuff import config_from_env, without_keys
from .route import Root
from .valid import YourssServerParameters

class Arguments(object):
	def __init__(self, argv):
		self.argv=argv
	def parse(self):
		import argparse
		parser = argparse.ArgumentParser(description='Start yourss server.')
		parser.add_argument('--host',      '-H', type=str,  help='host to listen')
		parser.add_argument('--port',      '-p', type=int,  help='port to listen')
		parser.add_argument('--debug',     '-d', type=bool, help='debug mode')
		parser.add_argument('--base-url',  '-b', type=str,  help='base url of yourss for link generation')
		parser.add_argument('--log-level', '-l', type=str,  help='log level', choices=logging._nameToLevel.keys())
		return parser.parse_args(self.argv).__dict__

class YourssServer(object):
	def __init__(self, host, port, debug, base_url):
		self._host=host
		self._port=port
		self._debug=debug
		self._base_url=base_url
	def __call__(self):
		# todo get rid of globality
		cherrypy.config.update({})
		cherrypy.config.update({
			'server.socket_host': self._host,
			'server.socket_port': self._port,
			'request.show_tracebacks': self._debug,
			'engine.autoreload.on': False})
		cherrypy.quickstart(Root(self._base_url))

def get_env_config():
	return config_from_env(
		host=('YOURSS_HOST', 'HOST'),
		port=('YOURSS_PORT', 'PORT'),
		debug=('YOURSS_DEBUG', 'DEBUG'),
		base_url=('YOURSS_BASE_URL', 'BASE_URL'),
		log_level=('YOURSS_LOG_LEVEL', 'LOG_LEVEL'))

def main(*args):
	config=get_env_config()
	config.update(Arguments(args).parse())
	logging.basicConfig(level=logging._nameToLevel.get(config['log_level'], logging.WARNING),
	                    handlers=[logging.StreamHandler()])
	YourssServerParameters(**without_keys(config, 'log_level')).valid_value().apply(YourssServer)()

if __name__=='__main__':
	from sys import argv
	main(*argv[1:])