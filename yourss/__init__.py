VERSION='0.1.0'

from os import environ as env

import cherrypy

from yourss.route import Root
from .stuff import Config, LazyWsgiApplication

# load env
envConfig=Config(env.get('HOST'), env.get('PORT'), env.get('DEBUG'), env.get('BASE_URL'))
envConfig=Config(env.get('YOURSS_HOST'), env.get('YOURSS_PORT'), env.get('YOURSS_DEBUG'), env.get('YOURSS_BASE_URL')).override(envConfig)

# for embedding
def start_server(host=None, port=None, debug=None, base_url=None):
	config=Config(host, port, debug, base_url).override(envConfig)
	cherrypy.config.update({
		'server.socket_host': config.host(),
		'server.socket_port': config.port(),
		'request.show_tracebacks': config.debug()})
	cherrypy.quickstart(Root(config.base_url()))