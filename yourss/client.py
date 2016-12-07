
from .valid import NonFalse, Default, PositiveInteger, ChoiceList, Quality, MediaType
from .youtube import Feed
from .text import UrlText

class Arguments(object):
	def __init__(self, argv):
		self.argv=argv
	def parse(self):
		import argparse
		parser = argparse.ArgumentParser(prog="yourss.client", description='Run yourss as local application.')
		parser.add_argument('--base-url',        '-b', type=str,  help='', required=True)
		parser.add_argument('--url',             '-u', type=str,  help='', required=True)
		parser.add_argument('--match_title',     '-m', type=int,  help='', default=None)
		parser.add_argument('--ignore_title',    '-i', type=int,  help='', default=None)
		parser.add_argument('--page-index',      '-p', type=str,  help='', default=1)
		parser.add_argument('--page-size',       '-s', type=str,  help='', default=100)
		parser.add_argument('--media-type',      '-t', type=str,  help='', choices=['audio', 'video'], default='video')
		parser.add_argument('--quality',         '-q', type=str,  help='', choices=['high', 'low'], default='high')
		parser.add_argument('--format',          '-f', type=str,  help='', default=None)
		parser.add_argument('--link-type',       '-l', type=str,  help='', choices=['dir    zect', 'webpage', 'proxy'], default='direct')
		parser.add_argument('--output',          '-o', type=str,  help='output file, - for stdout', default='-')
		return parser.parse_args(self.argv).__dict__

class Config(object):
	def __init__(self, base_url, url,
	             match_title=None, ignore_title=None,
	             page_index=1, page_size=100,
	             media_type='video', quality='high', format=None, link_type='direct',
	             output='-'):
		self._base_url=base_url
		self._url=url
		self._match_title=match_title
		self._ignore_title=ignore_title
		self._page_index=page_index
		self._page_size=page_size
		self._media_type=media_type
		self._quality=quality
		self._format=format
		self._link_type=link_type
		self._output=output
	def base_url(self):     return NonFalse(self._base_url, name='base_url').value()
	def url(self):          return NonFalse(self._url, name='url').value()
	def match_title(self):  return self._match_title
	def ignore_title(self): return self._ignore_title
	def page_index(self):   return PositiveInteger(self._page_index, name='page_index').value()
	def page_size(self):    return PositiveInteger(self._page_size, name='page_size').value()
	def media_type(self):   return MediaType(self._media_type).value()
	def quality(self):      return Quality(self._quality).value()
	def format(self):       return self._format
	def link_type(self):    return ChoiceList(Default(self._link_type, 'direct'), ('direct','webpage','proxy')).value()
	def output(self):       return Default(self._output, '-').value()

class FileWriter(object):
	def __init__(self, fileName):
		self.fileName=fileName
	def consume(self, iterable):
		import sys
		output=sys.stdout if '-'==self.fileName else open(self.fileName, 'w')
		try:
			was_error=False
			for chunk in iterable:
				if not was_error:
					try:
						output.write(chunk)
					except Exception as e:
						sys.stderr.write(str(e))
						was_error=True
		finally:
			if '-'!=self.fileName: output.close()

# for embedding
def run(base_url, url,
	    match_title=None, ignore_title=None, page_index=1, page_size=100,
	    media_type='video', quality='high', format=None, link_type='direct', output='-'):
	feed = Feed(base_url, UrlText(base_url, 'api', 'v1', 'feed').text(), UrlText(base_url, 'api', 'v1', 'episode').text(),
	            url, match_title, ignore_title, page_index, page_size,
	            media_type, quality, format, link_type)
	FileWriter(output).consume(feed.generate())

def main(*args):
	argd = Arguments(args).parse()
	config = Config(**argd)
	run(config.base_url(),
	     config.url(), config.match_title(), config.ignore_title(), config.page_index(), config.page_size(),
	     config.media_type(), config.quality(), config.format(), config.link_type(), config.output())

if __name__=='__main__':
	from sys import argv
	main(*argv[1:])