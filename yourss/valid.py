import re

class ParameterError(Exception):
	def __init__(self, code=400, message='client error', *args, **kwargs):
		self.code=code
		self.message=message
		Exception.__init__(self, *args, **kwargs)
	def __str__(self):
		return self.message

class Parameter(object):
	def __init__(self, value, code=400, name='parameter', message='{raw} is wrong value for {name}'):
		self._value=value
		self._code=code
		self._name=name
		self._message=message
	def code(self):
		if self._code: return self._code
		elif self._value and isinstance(self._value, Parameter): return self._value.code()
	def name(self):
		if self._name: return self._name
		elif self._value and isinstance(self._value, Parameter): return self._value.name()
	def message(self):
		if self._message: return self._message
		elif self._value and isinstance(self._value, Parameter) and self._value.message(): return self._value.message()
	def raw(self):
		return self._value.raw() if isinstance(self._value, Parameter) else self._value
	def valid(self):
		return True
	def error(self, code=None, message=None):
		raise ParameterError(
			code if code else self.code(),
			message if message else str(self.message()).format(name=self.name(), raw=self.raw()))
	def value(self):
		if not self.valid(): self.error()
		return self._value.value() if isinstance(self._value, Parameter) else self._value


class NonFalse(Parameter):
	def message(self):
		return '{name} must be non-null'
	def valid(self):
		return True if self.raw() else False

class Noneable(Parameter):
	def value(self):
		return None if (self.raw() is None) else Parameter.value(self)

class Default(Parameter):
	def __init__(self, data, default):
		Parameter.__init__(self, data)
		self.default = default
	def value(self):
		if self.raw() is None:
			return self.default.value() if isinstance(self.default, Parameter) else self.default
		else:
			return Parameter.value(self)

class PositiveInteger(Parameter):
	def value(self):
		try:
			result=int(self.raw())
		except ValueError:
			raise ParameterError(400, self._name + ' should be positive integer')
		if result < 1:
			raise ParameterError(400, self._name + ' should not be greater or equal to 1')
		return result

class Boolean(Parameter):
	def value(self):
		if   self.raw() in [True,  1, 'True',  'true',  'yes', '+', 'ok',  '1']: return True
		elif self.raw() in [False, 0, 'False', 'false', 'no',  '-', 'nie', '0']: return True
		else: self.error()

class Negated(Parameter):
	def __init__(self, boolean):
		self.boolean=boolean
	def raw(self):
		return self.boolean.raw()
	def value(self):
		return not self.boolean.value(self)

class ChoiceList(Parameter):
	def __init__(self, value, choice_list, name=None, message='{name} should be one of {choice_list}'):
		if message is None and not name is None:
			message = self._name + ' should be one of ' + str(self.choice_list)
		Parameter.__init__(self, value, name=name, message=message)
		if name is None: Parameter.__init__(self, value)
		else: Parameter.__init__(self, value, name)
		self.choice_list=choice_list
	def valid(self):
		return self.raw() in self.choice_list

class Regex(Parameter):
	def __init__(self, value, name='parameter', message='{name} is invalid regular expression'):
		Parameter.__init__(self, value, name=name, message=message)
	def valid(self):
		try:
			re.compile(self.raw())
		except:
			return False
		else:
			return True

class Audio(Noneable):
	def __init__(self, data):
		Noneable.__init__(self, Boolean(data, name='audio'))

class Quality(Parameter):
	def __init__(self, value, name='quality'):
		Parameter.__init__(self, Default(ChoiceList(value, ('high', 'low'), name=name), 'high'))

class PageIndex(Parameter):
	def __init__(self, value, name='page_index'):
		Parameter.__init__(self, Default(PositiveInteger(value, name=name), 1))

class PageSize(Parameter):
	def __init__(self, value, name='page_size'):
		Parameter.__init__(self, Default(PositiveInteger(value, name=name), 10))

class MediaType(Parameter):
	def __init__(self, value, name='page_size'):
		Parameter.__init__(self, Default(ChoiceList(value, ['video', 'audio'], name=name), 'video'))

class LinkType(Parameter):
	def __init__(self, value, name='page_size'):
		Parameter.__init__(self, Default(ChoiceList(value, ['direct', 'proxy', 'webpage'], name=name), 'direct'))

class MatchTitle(Parameter):
	def __init__(self, value, name='match_title'):
		Parameter.__init__(self, Noneable(Regex(value, name=name)))

class IgnoreTitle(Parameter):
	def __init__(self, value, name='ignore_title'):
		Parameter.__init__(self, Noneable(Regex(value, name=name)))


class UrlValidator(Parameter):
	def __init__(self, url=None, youtube=None, youtube_user=None, youtube_channel=None, youtube_playlist=None,
	             code=400, name='...', message='url not specified'):
		Parameter.__init__(self, None, code=code, name=name, message=message)
		self.url=url
		self.youtube=youtube
		self.youtube_user=youtube_user
		self.youtube_channel=youtube_channel
		self.youtube_playlist=youtube_playlist
		self.BASE = 'http://youtube.com/'
	def value(self):
		from urllib.request import quote
		if self.url:
			return self.url
		elif self.youtube:
			return self.BASE + 'watch?v=' + quote(self.youtube)
		elif self.youtube_user:
			return  self.BASE + 'user/' + quote(self.youtube_user)
		elif self.youtube_channel:
			return self.BASE + 'channel/' + quote(self.youtube_channel)
		elif self.youtube_playlist:
			return  self.BASE + 'playlist?list=' + quote(self.youtube_playlist)
		else:
			self.error()

