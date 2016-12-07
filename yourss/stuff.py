class InternalServerError(Exception):
		def __init__(self, code=500, message='client error', *args, **kwargs):
			self.code = code
			self.message = message
			Exception.__init__(self, *args, **kwargs)