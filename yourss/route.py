import cherrypy

from yourss.text import UrlText, PystacheArtifact, PystacheFileTemplate
from yourss.valid import ParameterException
from yourss.valid import FeedParameters, EpisodeParameters
from yourss.youtube import Feed as YoutubeFeed
from yourss.youtube import Episode as YoutubeEpisode

def Response(code, message):
	cherrypy.response.status = code
	cherrypy.response.headers['Content-Type'] = 'text/plain'
	return str(message)

class Route(object):
	def __init__(self, prefix, controller):
		if prefix is None or prefix in ('', '/'): self.prefix=()
		elif isinstance(prefix, str): self.prefix=(prefix,)
		else: self.prefix=prefix
		self.controller=controller
	def match(self, vpath):
		if len(vpath)>0:
			if len(vpath) < len(self.prefix):
				return False
			if '/'.join(vpath[:len(self.prefix)]) == '/'.join(self.prefix):
				return True
		elif self.prefix is None or 0==len(self.prefix, tuple): return True
		else: return False
	def pop_all(self, vpath):
		for i in self.prefix:
			vpath.pop(0)

class Router(object):
	def __init__(self, *routes):
		self.routes=routes
	def _cp_dispatch(self, vpath):
		for route in self.routes:
			if route.match(vpath):
				route.pop_all(vpath)
				return route.controller

class Episode(object):
	def __init__(self, yourss_base_url, base_url):
		self.yourss_base_url=yourss_base_url
		self.base_url=base_url
	@cherrypy.expose
	def index(self, url, media_type='audio', quality='low', format=None):
		try: arguments=EpisodeParameters(url, media_type=media_type, quality=quality, format=format).valid_value()
		except ParameterException as e: return Response(400, e.message)
		episode=arguments.apply(YoutubeEpisode)
		cherrypy.response.headers['Content-Type'] = episode.mimetype()
		cherrypy.response.headers['Content-Disposition'] = 'attachment; filename="' + episode.filename() + '"'
		filesize = episode.filesize()
		if filesize: cherrypy.response.headers['Content-Length']=str(filesize)
		return episode.generate()
	index._cp_config = {'response.stream': True}

class Feed(object):
	def __init__(self, yourss_base_url, feed_base_url, episode_base_url):
		self.yourss_base_url=yourss_base_url
		self.feed_base_url=feed_base_url
		self.episode_base_url=episode_base_url
	@cherrypy.expose
	def index(self, url, match_title=None, ignore_title=None,  page_index=1, page_size=10,
	          media_type='audio', quality='low', format=None, link_type='proxy',
	          title=None, thumbnail=None):
		cherrypy.response.headers['Content-Type']='text/xml'
		try:
			feed_parameters=FeedParameters(
				url=url, match_title=match_title, ignore_title=ignore_title, page_index=page_index, page_size=page_size,
				media_type=media_type, quality=quality, format=format, link_type=link_type,
				title=title, thumbnail=thumbnail,
				yourss_base_url=self.yourss_base_url, feed_base_url=self.feed_base_url, episode_base_url=self.episode_base_url).valid_value()
		except ParameterException as e:
			return Response(400, e.message)
		return feed_parameters.apply(YoutubeFeed).generate()

class ApiV1(Router):
	def __init__(self, yourss_base_url, base_url):
		self.yourss_base_url=yourss_base_url
		self.base_url=base_url
		feed=Feed(yourss_base_url=self.yourss_base_url,
				  feed_base_url=UrlText(self.base_url, 'feed').text(),
				  episode_base_url=UrlText(self.base_url, 'episode').text())
		episode=Episode(yourss_base_url=self.yourss_base_url,
		                base_url=UrlText(self.base_url, 'episode').text())
		Router.__init__(self, Route('feed', feed), Route('episode', episode))

class YoutubeRoute(Router):
	def __init__(self, yourss_base_url, base_url):
		Router.__init__(self)
		self.yourss_base_url=yourss_base_url
		self.base_url=base_url

	def _get_youtube_url(self, *args):
		raise Exception('not implemented')

	@cherrypy.expose
	def default(self, *args, match_title=None, ignore_title=None,  page_index=1, page_size=10,
	          media_type='audio', quality='low', format=None, link_type='proxy',
	          title=None, thumbnail=None):
		cherrypy.response.headers['Content-Type'] = 'text/xml'
		try:
			feed_parameters = FeedParameters(
				url=self._get_youtube_url(args), match_title=match_title, ignore_title=ignore_title, page_index=page_index, page_size=page_size,
				media_type=media_type, quality=quality, format=format, link_type=link_type,
				title=title, thumbnail=thumbnail,
				yourss_base_url=self.yourss_base_url, feed_base_url=UrlText(self.base_url, 'api', 'v1', 'feed').text(),
				episode_base_url=UrlText(self.yourss_base_url, 'api', 'v1', 'episode').text()).valid_value()
		except ParameterException as e:
			return Response(400, e.message)
		return feed_parameters.apply(YoutubeFeed).generate()

class YoutubeChannel(YoutubeRoute):
	def _get_youtube_url(self, parts):
		return 'https://www.youtube.com/channel/' + '/'.join(parts)

class YoutubeC(YoutubeRoute):
	def _get_youtube_url(self, parts):
		return 'https://www.youtube.com/c/' + '/'.join(parts)

class YoutubeUser(YoutubeRoute):
	def _get_youtube_url(self, parts):
		return 'https://www.youtube.com/user/' + '/'.join(parts)


class YoutubeSearch(Router):
	def __init__(self, yourss_base_url, base_url):
		Router.__init__(self)
		self.yourss_base_url=yourss_base_url
		self.base_url=base_url

	@cherrypy.expose
	def default(self, search_query, match_title=None, ignore_title=None,  page_index=1, page_size=10,
	          media_type='audio', quality='low', format=None, link_type='proxy',
	          title=None, thumbnail=None):
		cherrypy.response.headers['Content-Type'] = 'text/xml'
		try:
			# todo escape search_query
			feed_parameters = FeedParameters(
				url='https://www.youtube.com/results?search_query=' + search_query, match_title=match_title, ignore_title=ignore_title, page_index=page_index, page_size=page_size,
				media_type=media_type, quality=quality, format=format, link_type=link_type,
				title=title, thumbnail=thumbnail,
				yourss_base_url=self.yourss_base_url, feed_base_url=UrlText(self.base_url, 'api', 'v1', 'feed').text(),
				episode_base_url=UrlText(self.base_url, 'api', 'v1', 'episode').text()).valid_value()
		except ParameterException as e:
			return Response(400, e.message)
		return feed_parameters.apply(YoutubeFeed).generate()


class Root(Router):
	def __init__(self, base_url):
		self.base_url=base_url
		Router.__init__(self,
			self._create_route(ApiV1, 'api', 'v1'),
			self._create_route(YoutubeChannel, 'channel'),
			self._create_route(YoutubeC, 'c'),
			self._create_route(YoutubeUser, 'user'),
			self._create_route(YoutubeSearch, 'results'))

	def _create_route(self, factory, *parts):
		return Route(parts, factory(self.base_url, base_url=UrlText(self.base_url, *parts).text()))

	@cherrypy.expose
	def index(self):
		return PystacheArtifact(PystacheFileTemplate('index'), BASE_URL=self.base_url).text()