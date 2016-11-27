
class Arguments(object):
	def __init__(self):
		pass
	def parse(self):
		import argparse
		parser = argparse.ArgumentParser(description='Start yourss server.')
		parser.add_argument('--host',  '-H', type=str,  help='host to listen', default='127.0.0.1')
		parser.add_argument('--port',  '-p', type=int,  help='port to listen', default=80)
		parser.add_argument('--debug', '-d', type=bool, help='debug mode',     default=False)
		parser.add_argument('--base-url', '-b', type=str, help='base url of yourss for link generation',  default=None)
		return parser.parse_args().__dict__
			
		


from . import start_server
start_server(**(Arguments().parse()))