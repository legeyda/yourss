

from os.path import dirname, abspath, join
from functools import reduce
import urllib
import urllib.parse
from pystache import render


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

class PystacheArtifact(Text):
	def __init__(self, *args):
		self.parts=args[:-1]
		self.context=args[-1]
	def text(self):
		return render(PypathTextFile('template', *self.parts), self.context)

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
		for key in self.params.keys():
			parts.append(str(key) + '=' + UrlEscape(str(self.params[key])).text())
		string='&'.join(parts)
		return '?' + string if string else ''

class UrlEscape(Text):
	def __init__(self, string):
		self.string=string
	def text(self):
		return urllib.parse.quote(self.string, safe='')

