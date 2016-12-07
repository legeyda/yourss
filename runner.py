
def main(*args):
	if   len(args)>0 and "server" == args[0]:
		from yourss.server import main
		main(*args[1:])
	elif len(args)>0 and "client" == args[0]:
		from yourss.client import main
		main(*args[1:])
	elif len(args)>0 and "test" == args[0]:
		from unittest import main
		main(module='testyourss')
	else:
		print('Usage: server or client or test')

if '__main__' == __name__:
	from sys import argv
	main(*argv[1:])




