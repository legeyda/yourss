import os

class InternalServerError(Exception):
		def __init__(self, code=500, message='client error', *args, **kwargs):
			self.code = code
			self.message = message
			Exception.__init__(self, *args, **kwargs)

def config_from_env(**names):
	result={}
	for (key, vars) in names.items():
		if not isinstance(vars, (tuple, list)): vars=(vars,)
		for var in vars: result[key]=os.environ.get(var)
	return result




def without_keys(dic, *keys):
	result={}
	result.update(dic)
	for key in keys: del result[key]
	return result
