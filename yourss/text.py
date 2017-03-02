

from os.path import dirname, abspath, join
from functools import reduce
import urllib
import urllib.parse
from pystache import render
from . import VERSION


class Text(object):
	def text(self):
		return ''
	def __str__(self):
		return self.text()

class TextFile(Text):
	def __init__(self, path):
		self.path=path
	def text(self):
		return "\n".join(open(self.path).readlines())

class PypathTextFile(TextFile):
	def __init__(self, *parts):
		TextFile.__init__(self, join(dirname(abspath(__file__)), *parts))

class PystacheFileTemplate(PypathTextFile):
	def __init__(self, *parts):
		super().__init__(*(['template'] + list(parts)[:-1] + [(parts[-1] + '.mustache')]))

class ParameterizedText(Text):
	def with_context(self, **context):
		pass

class PystacheArtifact(ParameterizedText):
	def __init__(self, template, **context):
		self._template=template
		self._context={'YOURSS_VERSION': VERSION}
		self._context.update(context)
	def with_context(self, **context):
		new_context={}
		new_context.update(self._context)
		new_context.update(context)
		return PystacheArtifact(self._template, **new_context)
	def text(self):
		return render(str(self._template), self._context)

class JoinedPystacheArtifacts(ParameterizedText):
	def __init__(self, separator, *artifacts):
		self._separator=separator
		self._artifacts=artifacts
	def with_context(self, **context):
		self._artifacts=[a.with_context(context) for a in self._artifacts]
	def text(self):
		return str(self._separator).join([a.text() for a in self._artifacts])

class UrlText(Text):
	def __init__(self, *parts):
		self.parts=parts
	def trim_left(self, string, char):
		string=str(string)
		while string.endswith(char):
			string=string[:-1]
		return string
	def trim_right(self, string, char):
		string=str(string)
		while string.startswith(char):
			string=string[1:]
		return string
	def text(self):
		return reduce(lambda x,y: self.trim_right(x, '/') + '/' + self.trim_left(y, '/'), self.parts)

class UrlQuery(Text):
	def __init__(self, **kwargs):
		self.params=kwargs
	def text(self):
		parts=[]
		for key in sorted(self.params.keys()):
			if self.params[key]:
				parts.append(str(key) + '=' + UrlEscape(str(self.params[key])).text())
		string='&'.join(parts)
		return '?' + string if string else ''

class UrlEscape(Text):
	def __init__(self, string):
		self.string=string
	def text(self):
		return urllib.parse.quote(self.string, safe='')

