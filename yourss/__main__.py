

from os import environ as env


def main(*args):
	USAGE='Usage: yourss [-h|--help|server|client|gui]'
	if   2==len(args) and args[1] in ('-h', '--help'):
		print(USAGE)
	elif 0<len(args) and 'server' == args[0]:
		from . import server
		server.main(*args[1:])
	elif 0<len(args) and 'client' == args[0]:
		from . import client
		client.main(*args[1:])
	elif 0==len(args) or 'gui' == args[0]:
		from . import gui
		gui.main(*args[1:])
	else:
		import sys
		print('wrong arguments')
		print(USAGE)
		sys.exit(1)



if '__main__' == __name__:
	from sys import argv
	main(*argv[1:])

