import re

from .text import PystacheArtifact, JoinedPystacheArtifacts, UrlText

class Default(object):
	def __init__(self, parameter): self._parameter=parameter
	def value(self): return self._parameter(None).valid_value()

def default_value(parameter):
	return Default(parameter).value()

class ParameterException(Exception):
	def __init__(self, message, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.message=message
	def __str__(self):
		return str(self.message)

class Parameter(object):
	"""parameter interface"""
	def value(self):
		"""raw value of parameter it can be either valid or not"""
	def valid_value(self, exception_type=ParameterException, *args, **kwargs):
		"""valid value, or raises exception_type(*args, **kwargs)"""
	def message(self):
		"""if value is not valid messages about it, else None"""

class ValidValue(Parameter):
	def __init__(self, value): self._value=value
	def value(self): return self._value
	def valid_value(self, exception_type=ParameterException, *args, **kwargs): return self.value()

class ParameterWrapper(Parameter):
	def __init__(self, wrapped): self._wrapped=wrapped
	def wrapped(self): return self._wrapped
	def value(self): return self._wrapped.value()
	def valid_value(self, exception_type=ParameterException, *args, **kwargs):
		return self._wrapped.valid_value(exception_type, *args, **kwargs)
	def message(self): return self._wrapped.message()

class TitledParameter(ParameterWrapper):
	def __init__(self, wrapped, title='parameter'):
		super().__init__(wrapped)
		self._title=title
	def with_context(self, message):
		return message.with_context(title=self._title)
	def valid_value(self, exception_type=ParameterException, *args, **kwargs):
		try:
			return self.wrapped().valid_value(exception_type, *args, **kwargs)
		except exception_type as e:
			e.message=self.with_context(e.message)
			raise e
	def message(self): return self.with_context(self.wrapped().message())

class BaseParameter(Parameter):
	def __init__(self, data):
		self._data=data if isinstance(data, Parameter) else ValidValue(data)
	def data(self): return self._data
	def value(self): return self.data().value()
	def const_message(self): return PystacheArtifact('wrong value for {{#title}}parameter {{title}}{{/title}}{{^title}}parameter{{/title}}')
	def throw(self, message, exception_type=ParameterException, *args, **kwargs):
		raise exception_type(self.const_message(), exception_type, *args, **kwargs)

class CheckingBaseParameter(BaseParameter):
	"""to avoid stack overflow, must override either valid or message"""
	def valid(self): return not self.message()
	def message(self):
		if not self.valid(): return self.const_message()
	def valid_value(self, exception_type=ParameterException, *args, **kwargs):
		message=self.message()
		if message: self.throw(exception_type, *args, **kwargs)
		return self.value()

class TransformingBaseParameter(BaseParameter):
	def valid(self):
		return not self.message()
	def message(self):
		try: self.valid_value()
		except ParameterException as e: return e.message

class TextParameter(TransformingBaseParameter):
	def valid_value(self, exception_type=ParameterException, *args, **kwargs):
		return str(self.value()) if self.value() else ''

class UrlStringParameter(ParameterWrapper):
	def __init__(self, url_string):
		super().__init__(TextParameter(url_string))

class IntegerParameter(TransformingBaseParameter):
	def default_message(self):
		return PystacheArtifact('{{title}}{{^title}}value{{/title}} should be integer')
	def valid_value(self, exception_type=ParameterException, *args, **kwargs):
		value=self.value()
		try: return int(value)
		except Exception: self.throw(exception_type, *args, **kwargs)

class PositiveIntegerParameter(TransformingBaseParameter):
	def default_message(self):
		return PystacheArtifact('{{title}}{{^title}}value{{/title}} should be positive')
	def valid_value(self, exception_type=ParameterException, *args, **kwargs):
		result=IntegerParameter(self.data().valid_value()).valid_value(exception_type, *args, **kwargs)
		if result < 1: self.throw(exception_type, *args, **kwargs)
		return result

class BooleanParameter(TransformingBaseParameter):
	def default_message(self):
		return PystacheArtifact('{{title}}{{^title}}value{{/title}} does not look like boolean')
	def valid_value(self, exception_type=ParameterException, *args, **kwargs):
		if   self.data().valid_value() in [True,  1, 'True',  'true',  'yes', '+', 'ok',  '1']: return True
		elif self.data().valid_value() in [False, 0, 'False', 'false', 'no',  '-', 'nie', '0']: return False
		else: self.throw(exception_type, *args, **kwargs)

class StringParameter(TransformingBaseParameter):
	def valid_value(self, exception_type=ParameterException, *args, **kwargs):
		return None if self.value() is None else str(self.value())

class ChoiceListParameter(CheckingBaseParameter):
	def __init__(self, data, choice_list):
		super().__init__(data)
		self._choice_list=choice_list
	def valid(self):
		return self.value() in self._choice_list

class NonEmptyParameter(CheckingBaseParameter):
	def valid(self): return self.data().valid_value() is not None and ''!=self.data().valid_value()

class DefaultValuedParameter(TransformingBaseParameter):
	def __init__(self, data, default_value):
		super().__init__(data)
		self._default_value=default_value
	def valid_value(self, exception_type=ParameterException, *args, **kwargs):
		if self.data().valid_value() is None or '' == self.data().valid_value(): return self._default_value
		return self.data().valid_value()

class DefaultFactoryValuedParameter(TransformingBaseParameter):
	def __init__(self, data, default_value_factory):
		super().__init__(data)
		self._default_value_factory=default_value_factory
	def valid_value(self, exception_type=ParameterException, *args, **kwargs):
		if self.value() is None or '' == self.value(): return self._default_value_factory()
		return self.data().valid_value()

class RegexStringParameter(CheckingBaseParameter):
	def valid(self):
		try:    re.compile(str(self.data().valid_value()))
		except: return False
		else:   return True

class FunctionArguments(object):
	def __init__(self, *args, **kwargs):
		self._args=list(args)
		self._kwargs=dict(kwargs)
	def args(self): return self._args
	def kwargs(self): return self._kwargs
	def apply(self, func):
		return func(*self.args(), **self.kwargs())
	def __getitem__(self, key):
		if   isinstance(key, int): return self.args()[key]
		elif isinstance(key, str): return self.kwargs()[key]
		raise KeyError()
	def __iter__(self):
		return iter(self.args() + list(self.kwargs().keys()))
	def map(self, func):
		return FunctionArguments(*[func(a) for a in self.args()], **{k:func(a) for (k,a) in self.kwargs().items()})
	def add(self, *args, **kwargs):
		new_kwargs={}
		new_kwargs.update(self.kwargs())
		new_kwargs.update(kwargs)
		return FunctionArguments(self.args() + args, new_kwargs)

class Factory(object):
	def __init__(self, constructor, *args, **kwargs):
		self._constructor=constructor
		if 0==len(kwargs) and 1==len(args) and isinstance(args[0], FunctionArguments):
			self._arguments=args[0]
		else:
			self._arguments=FunctionArguments(*args, **kwargs)
	def __call__(self, *ignored_args, **ignored_kwargs):
		return self._arguments.apply(self._constructor)

class FunctionParameters(TransformingBaseParameter):
	def __init__(self, *args, **kwargs):
		if 0==len(kwargs) and 1==len(args) and isinstance(args[0], FunctionArguments):
			super().__init__(args[0])
		else:
			super().__init__(FunctionArguments(*args, **kwargs))
	def valid_value(self, exception_type=ParameterException, *args, **kwargs):
		messages = []
		def mapper(param):
			try:
				return param.valid_value()
			except ParameterException as e:
				messages.append(e.message)
		result=self.data().value().map(mapper)
		if messages:
			raise exception_type(JoinedPystacheArtifacts(', ', *messages))
		return result















class YourssBaseUrlParameter(ParameterWrapper):
	def __init__(self, yourss_base_url):
		super().__init__(TitledParameter(UrlStringParameter(yourss_base_url), title='yourss base url'))


# ======== server parameters ========

class HostParameter(ParameterWrapper):
	def __init__(self, value):
		super().__init__(TitledParameter(DefaultValuedParameter(value, '127.0.0.1'), title='host'))

class PortParameter(ParameterWrapper):
	def __init__(self, value):
		super().__init__(TitledParameter(PositiveIntegerParameter(DefaultValuedParameter(value, '80')), title='port'))

class DebugParameter(ParameterWrapper):
	def __init__(self, value):
		super().__init__(TitledParameter(BooleanParameter(DefaultValuedParameter(value, False)), title='debug enabled'))

class YourssServerParameters(ParameterWrapper):
	def __init__(self, host, port, debug, base_url):
		host_parameter = HostParameter(host)
		port_parameter = PortParameter(port)
		super().__init__(FunctionParameters(FunctionArguments(
			host=host_parameter,
			port=port_parameter,
			debug=DebugParameter(debug),
			base_url=TitledParameter(DefaultFactoryValuedParameter(YourssBaseUrlParameter(base_url),
				default_value_factory=lambda: 'http://' + str(host_parameter.valid_value()) + ':' + str(port_parameter.valid_value())), title='base url')
		)))




# ======== feed (client) parameters ========

default_feed_parameter_values={
	'match_title': '',
	'ignore_title': '',
	'page_index': 1,
	'page_size': 10,
	'media_type': 'audio',
	'quality': 'low',
	'link_type': 'direct'
}

class OutputParameter(ParameterWrapper):
	def __init__(self, value):
		super().__init__(TitledParameter(NonEmptyParameter(TextParameter(value)), title='output'))


class UrlParameter(ParameterWrapper):
	def __init__(self, url):
		super().__init__(TitledParameter(NonEmptyParameter(url), title='base url'))


class MatchTitleParameter(ParameterWrapper):
	def __init__(self, match_title):
		super().__init__(TitledParameter(TextParameter(match_title), title='match title'))


class IgnoreTitleParameter(ParameterWrapper):
	def __init__(self, match_title):
		super().__init__(TitledParameter(TextParameter(match_title), title='ignore title'))


class PageIndexParameter(ParameterWrapper):
	def __init__(self, page_index):
		super().__init__(
			TitledParameter(PositiveIntegerParameter(DefaultValuedParameter(page_index, default_feed_parameter_values['page_index'])), title='page index'))


class PageSizeParameter(ParameterWrapper):
	def __init__(self, page_index):
		deafult_page_size=default_feed_parameter_values['page_size']
		super().__init__(
			TitledParameter(PositiveIntegerParameter(DefaultValuedParameter(page_index, deafult_page_size)), title='page size'))


class MediaTypeParameter(ParameterWrapper):
	def __init__(self, media_type):
		super().__init__(
			TitledParameter(ChoiceListParameter(DefaultValuedParameter(media_type, default_feed_parameter_values['media_type']), ('audio', 'video')),
							title='media type'))


class QualityParameter(ParameterWrapper):
	def __init__(self, quality):
		super().__init__(TitledParameter(ChoiceListParameter(DefaultValuedParameter(quality, default_feed_parameter_values['quality']), ('low', 'high')),
										 title='quality'))


class FormatParameter(ParameterWrapper):
	def __init__(self, format):
		super().__init__(TitledParameter(ValidValue(format), title='format'))


class LinkTypeParameter(ParameterWrapper):
	def __init__(self, link_type):
		super().__init__(TitledParameter(ChoiceListParameter(DefaultValuedParameter(link_type, default_feed_parameter_values['link_type']), ('direct', 'webpage', 'proxy')), title='link type'))


class TitleParameter(ParameterWrapper):
	def __init__(self, title):
		super().__init__(TitledParameter(TextParameter(title), title='override title'))


class ThumbnailParameter(ParameterWrapper):
	def __init__(self, thumbnail):
		super().__init__(TitledParameter(TextParameter(thumbnail), title='override thumbnail'))


class FeedBaseUrlParameter(ParameterWrapper):
	def __init__(self, feed_base_url):
		super().__init__(TitledParameter(UrlStringParameter(feed_base_url), title='feed base url'))

class EpisodeBaseUrlParameter(ParameterWrapper):
	def __init__(self, episode_base_url):
		super().__init__(TitledParameter(UrlStringParameter(episode_base_url), title='episode base url'))



class FeedParameters(TransformingBaseParameter):
	def __init__(self, url,
				 match_title=None, ignore_title=None, page_index=1, page_size=100,
				 media_type='video', quality='high', format=None, link_type='direct',
				 title=None, thumbnail=None,
				 yourss_base_url=None, feed_base_url=None, episode_base_url=None):
		yourss_base_url = YourssBaseUrlParameter(yourss_base_url)
		super().__init__(FunctionParameters(FunctionArguments(
			url=UrlParameter(url),
			match_title=MatchTitleParameter(match_title),
			ignore_title=IgnoreTitleParameter(ignore_title),
			page_index=PageIndexParameter(page_index),
			page_size=PageSizeParameter(page_size),
			media_type=MediaTypeParameter(media_type),
			quality=QualityParameter(quality),
			format=FormatParameter(format),
			link_type=LinkTypeParameter(link_type),
			title=TitleParameter(title),
			thumbnail=ThumbnailParameter(thumbnail),
			yourss_base_url=yourss_base_url,
			feed_base_url=DefaultFactoryValuedParameter(
				FeedBaseUrlParameter(feed_base_url),
				default_value_factory=lambda: UrlText(yourss_base_url.valid_value(), 'api', 'v1', 'feed').text()),
			episode_base_url=DefaultFactoryValuedParameter(
				EpisodeBaseUrlParameter(episode_base_url),
				default_value_factory=lambda: UrlText(yourss_base_url.valid_value(), 'api', 'v1', 'episode').text()),
		)))

	def valid_value(self, exception_type=ParameterException, *args, **kwargs):
		result = self.data().valid_value(exception_type, *args, **kwargs)
		if 'proxy' == result['link_type'] and not result['episode_base_url']:
			raise exception_type('clip base url should be set when link type is proxy', *args, **kwargs)
		return result

class EpisodeParameters(ParameterWrapper):
	def __init__(self, url, media_type='video', quality='high', format=None):
		super().__init__(FunctionParameters(
			url=UrlParameter(url),
			media_type=MediaTypeParameter(media_type),
			quality=QualityParameter(quality),
			format=FormatParameter(format)
		))

class ClientParameters(TransformingBaseParameter):
	def __init__(self, output, url,
				 match_title=None, ignore_title=None, page_index=1, page_size=10,
				 media_type='video', quality='high', format=None, link_type='direct',
				 title=None, thumbnail=None,
				 yourss_base_url=None, feed_base_url=None, episode_base_url=None):
		super().__init__(FeedParameters(url, match_title, ignore_title, page_index, page_size,
		                                media_type, quality, format, link_type, title, thumbnail,
		                                yourss_base_url, feed_base_url, episode_base_url))
		self._output_parameter=OutputParameter(output)
	def valid_value(self, exception_type=ParameterException, *args, **kwargs):
		return self.data().valid_value(exception_type, *args, **kwargs)\
			.add(output=self._output_parameter.valid_value(exception_type, *args, **kwargs))





