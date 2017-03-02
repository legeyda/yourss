import os

class InternalServerError(Exception):
		def __init__(self, code=500, message='client error', *args, **kwargs):
			self.code = code
			self.message = message
			Exception.__init__(self, *args, **kwargs)


#class EnvVar(Text):
#	pass

def value_from_env(*names):
	result=None
	for name in names:
		if name in os.environ.keys():
			return os.environ.get(name)
	return

def config_from_env(**names):
	result={}
	for (key, vars) in names.items():
		if not isinstance(vars, (tuple, list)): vars = (vars,)
		result[key]=value_from_env(*vars)
	return result


def without_keys(dic, *keys):
	result={}
	result.update(dic)
	for key in keys: del result[key]
	return result
