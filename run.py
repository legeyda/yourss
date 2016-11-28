import logging
logging.basicConfig(level=logging.DEBUG, handlers=[logging.StreamHandler()])
logging.getLogger(__file__).error('testyourss error')


from sys import argv
if len(argv)>1:
	if "run" == argv[1]:
		from yourss import start_server
		start_server(port=8081, debug=True)
	elif "test" == argv[1]:
		from unittest import main
		main(module='testyourss')






