import logging
logging.basicConfig(level=logging.DEBUG, handlers=[logging.StreamHandler()])


from sys import argv
if   len(argv)>1 and "run" == argv[1]:
	from yourss import start_server
	start_server(port=8081, debug=True)
elif len(argv)>1 and "test" == argv[1]:
	from unittest import main
	main(module='testyourss')
else:
	print('Usage: run or test')






