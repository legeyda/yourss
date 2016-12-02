import logging
from os import environ

import cherrypy

from .stuff import Arguments

args=Arguments(environ).parse()
cherrypy.config.update({'engine.autoreload.on': False})

# configure log
logging.basicConfig(level=logging._nameToLevel.get(args['log_level'], logging.WARNING), handlers=[logging.StreamHandler()])
logging.getLogger(__name__).error('testyourss error')

# start server
from . import start_server
start_server(host=args['host'], port=args['port'], debug=args['debug'], base_url=args['base_url'])