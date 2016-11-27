import cherrypy
from .cherry import Root

def start_server(host='127.0.0.1', port=80, debug=True, base_url=None):
	if not base_url:
		base_url='http://' + host + ':' + str(port)
	cherrypy.config.update({
		'server.socket_host': host,
		'server.socket_port': port,
		'request.show_tracebacks': debug})
	cherrypy.quickstart(Root(base_url))