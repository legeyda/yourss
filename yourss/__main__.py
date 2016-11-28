

import logging

class Arguments(object):
	def __init__(self):
		pass
	def parse(self):
		import argparse
		parser = argparse.ArgumentParser(description='Start yourss server.')
		parser.add_argument('--host',      '-H', type=str,  help='host to listen', default='127.0.0.1')
		parser.add_argument('--port',      '-p', type=int,  help='port to listen', default=80)
		parser.add_argument('--debug',     '-d', type=bool, help='debug mode',     default=False)
		parser.add_argument('--base-url',  '-b', type=str,  help='base url of yourss for link generation',  default=None)
		parser.add_argument('--log-level', '-l', type=str,  help='log level',  default='WARNING', choices=logging._nameToLevel.keys())
		return parser.parse_args().__dict__

args=Arguments().parse()

# configure log
logging.basicConfig(level=logging._nameToLevel.get(args['log_level'], logging.WARNING), handlers=[logging.StreamHandler()])
logging.getLogger(__name__).error('testyourss error')


import cherrypy
cherrypy.config.update({'engine.autoreload.on': False})

from . import start_server
start_server(host=args['host'], port=args['port'], debug=args['debug'], base_url=args['base_url'])