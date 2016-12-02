import cherrypy

from yourss.text import UrlText, PystacheArtifact
from yourss.valid import Noneable, ParameterError, Quality, PageIndex, PageSize, MediaType, LinkType, MatchTitle, IgnoreTitle
from yourss.youtube import Episode as YoutubeEpisode
from yourss.youtube import Feed as YoutubeFeed


def Response(code, message):
	cherrypy.response.status = code
	cherrypy.response.headers['Content-Type'] = 'text/plain'
	return message

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
	def index(self, url, media_type='video', quality='high', format_=None):
		youtube_video=YoutubeEpisode(
			url,
			media_type=MediaType(media_type).value(),
			quality=Quality(quality).value(),
			format_=format_,)
		cherrypy.response.headers['Content-Type'] = youtube_video.mimetype()
		return youtube_video.generate()




class Feed(object):
	def __init__(self, yourss_base_url, base_url, clip_base_url):
		self.yourss_base_url=yourss_base_url
		self.base_url=base_url
		self.clip_base_url=clip_base_url
	@cherrypy.expose
	def index(self, url, match_title=None, ignore_title=None,  page_index=1, page_size=10,
	          media_type='video', quality='high', format=None, link_type='direct'):
		cherrypy.response.headers['Content-Type']='text/xml'
		try:
			return YoutubeFeed(
			    yourss_base_url=self.yourss_base_url,
			    base_url=self.base_url,
			    clip_base_url=self.clip_base_url,
				url=url,
				match_title=MatchTitle(match_title, name='match_title').value(),
				ignore_title=IgnoreTitle(ignore_title, name='ignore_title').value(),
				page_index=PageIndex(page_index).value(),
				page_size=PageSize(page_size).value(),
			    media_type=MediaType(media_type).value(),
			    quality=Quality(quality).value(),
			    format=format,
				link_type=LinkType(link_type).value(),
			).generate()
		except ParameterError as e:
			return Response(e.code, e.message)




class Yourss(Router):
	def __init__(self, yourss_base_url, base_url):
		self.yourss_base_url=yourss_base_url
		self.base_url=base_url
		Router.__init__(self,
			Route('feed', Feed(
					yourss_base_url=self.yourss_base_url,
					base_url=UrlText(self.base_url, 'feed').text(),
					clip_base_url=UrlText(self.base_url, 'episode').text())),
			Route('episode', Episode(
					yourss_base_url=self.yourss_base_url,
					base_url=UrlText(self.base_url, 'episode').text()))
		)



class Root(Router):
	def __init__(self, base_url):
		self.base_url=base_url
		parts=('api', 'v1')
		Router.__init__(self, Route(parts, Yourss(self.base_url, base_url=UrlText(self.base_url, *parts).text())))
	@cherrypy.expose
	def index(self):
		return PystacheArtifact('index.mustache', {'base_url': self.base_url}).text()