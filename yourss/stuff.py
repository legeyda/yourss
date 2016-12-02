
from .valid import Default, PositiveInteger, Boolean

class Arguments(object):
	def __init__(self, environ):
		self.environ=environ
	def parse(self):
		import argparse
		parser = argparse.ArgumentParser(description='Start yourss server.')
		parser.add_argument('--host',      '-H', type=str,  help='host to listen')
		parser.add_argument('--port',      '-p', type=int,  help='port to listen')
		parser.add_argument('--debug',     '-d', type=bool, help='debug mode')
		parser.add_argument('--base-url',  '-b', type=str,  help='base url of yourss for link generation')
		parser.add_argument('--log-level', '-l', type=str,  help='log level', choices=logging._nameToLevel.keys())
		return parser.parse_args(self.environ).__dict__


class Config(object):
	def __init__(self, host, port, debug, base_url):
		self._host=host
		self._port=port
		self._debug=debug
		self._base_url=base_url
	def host(self):
		return self._host if self._host else '127.0.0.1'
	def port(self):
		return Default(PositiveInteger(self._port, name='port'), 80).value()
	def debug(self):
		return Default(Boolean(self._debug, name='debug'), False).value()
	def base_url(self):
		if self._base_url: return self._base_url
		else: return 'http://' + self.host() + ':' + str(self.port())
	def override(self, base):
		return Config(
			self.host()     if self.host()     else base.host(),
			self.port()     if self.port()     else base.port(),
			self.debug()    if self.debug()    else base.debug(),
			self.base_url() if self.base_url() else base.base_url())

class LazyWsgiApplication(object):
	def __init__(self, application_factory):
		self.application_factory=application_factory
		self.application=None
	def __call__(self, environ, start_response):
		if self.application is None:
			self.application = self.application_factory()
		return self.application(environ, start_response)

class InternalServerError(Exception):
		def __init__(self, code=500, message='client error', *args, **kwargs):
			self.code = code
			self.message = message
			Exception.__init__(self, *args, **kwargs)