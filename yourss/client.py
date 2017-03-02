from yourss.stuff import config_from_env, without_keys
from .text import UrlText
from .valid import FeedParameters, OutputParameter, default_feed_parameter_values
from .youtube import Feed

class CommandLineArguments(object):
	def __init__(self, argv):
		self.argv=argv
	def parse(self):
		import argparse
		parser = argparse.ArgumentParser(prog="yourss.client", description='Run yourss as local application.')
		parser.add_argument('--base-url',     '-b', type=str,  help='', required=True, dest='yourss_base_url')
		parser.add_argument('--url',          '-u', type=str,  help='', required=True)
		parser.add_argument('--match-title',  '-m', type=int,  help='', default=None)
		parser.add_argument('--ignore-title', '-i', type=int,  help='', default=None)
		parser.add_argument('--page-index',   '-p', type=str,  help='', default=default_feed_parameter_values['page_index'])
		parser.add_argument('--page-size',    '-s', type=str,  help='', default=default_feed_parameter_values['page_size'])
		parser.add_argument('--media-type',   '-t', type=str,  help='', choices=['audio', 'video'], default=default_feed_parameter_values['media_type']),
		parser.add_argument('--quality',      '-q', type=str,  help='', choices=['high', 'low'], default=default_feed_parameter_values['quality']),
		parser.add_argument('--format',       '-f', type=str,  help='', default=None)
		parser.add_argument('--link-type',    '-l', type=str,  help='', choices=['direct', 'webpage', 'proxy'], default=default_feed_parameter_values['link_type']),
		parser.add_argument('--title',              type=str,  help='', default=None)
		parser.add_argument('--thumbnail',          type=str,  help='', default=None)
		parser.add_argument('--output',       '-o', type=str,  help='output file, - for stdout', default='-')
		return parser.parse_args(self.argv).__dict__

class FileWriter(object):
	def __init__(self, file_name):
		self.file_name=file_name
	def consume(self, iterable):
		import sys
		output=None
		try:
			# todo create dirs
			output = sys.stdout.buffer if '-' == self.file_name else open(self.file_name, 'wb')
			was_error=False
			for chunk in iterable:
				if not was_error:
					try:
						if   isinstance(chunk, str):   output.write(chunk.encode('UTF-8'))
						elif isinstance(chunk, bytes): output.write(chunk)
						else: raise Exception('wrong type chun')
					except Exception as e:
						sys.stderr.write(str(e))
						was_error=True
		finally:
			if output and '-'!=self.file_name: output.close()


# for embedding
def generate_feed(base_url, url,
                  match_title=None, ignore_title=None, page_index=1, page_size=10,
                  media_type='video', quality='high', format=None, link_type='direct',
                  title=None, thumbnail=None,
                  output='-'):
	feed = Feed(url, match_title, ignore_title, page_index, page_size,
	            media_type, quality, format, link_type, title, thumbnail,
				base_url, UrlText(base_url, 'api', 'v1', 'feed').text(),
				UrlText(base_url, 'api', 'v1', 'episode').text())
	FileWriter(output).consume(feed.generate())

def main(*args):
	config=config_from_env(
		url          = ('URL', 'YOURSS_URL'),
		match_title  = ('MATCH_TITLE', 'YOURSS_MATCH_TITLE'),
		ignore_title = ('IGNORE_TITLE', 'YOURSS_IGNORE_TITLE'),
		page_index   = ('PAGE_INDEX', 'YOURSS_PAGE_INDEX'),
		page_size    = ('PAGE_SIZE', 'YOURSS_PAGE_SIZE'),
		media_type   = ('MEDIA_TYPE', 'YOURSS_MEDIA_TYPE'),
		quality      = ('QUALITY', 'YOURSS_QUALITY'),
		format       = ('FORMAT', 'YOURSS_FORMAT'),
		link_type    = ('LINK_TYPE', 'YOURSS_LINK_TYPE'),
		title        = ('TITLE', 'YOURSS_TITLE'),
		thumbnail    = ('THUMBNAIL', 'YOURSS_THUMBNAIL'),
		output       = ('OUTPUT', 'YOURSS_OUTPUT')
	)
	config.update(CommandLineArguments(args).parse())
	feed=FeedParameters(**without_keys(config, 'output')).valid_value().apply(Feed)
	FileWriter(OutputParameter(config['output']).valid_value()).consume(feed.generate())

if __name__=='__main__':
	from sys import argv
	main(*argv[1:])
