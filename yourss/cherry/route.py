import cherrypy
from yourss.youtube import Feed as YoutubeFeed
from yourss.youtube import Episode as YoutubeEpisode
from yourss.text import UrlText, PypathTextFile, PystacheArtifact
from .validator import ParameterError, Audio, Quality, PageIndex, PageSize

def Response(code, message):
	cherrypy.response.status = code
	cherrypy.response.headers['Content-Type'] = 'text/plain'
	return message

class Route(object):
	def __init__(self, prefix, controller):
		if prefix is None or prefix in ('', '/'): self.prefix=()
		elif isinstance(prefix, str): self.prefix='/'.split(prefix)
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
	def __init__(self, yourss_base_url, base_url, audio=False):
		self.yourss_base_url=yourss_base_url
		self.base_url=base_url
		self.audio=audio
	@cherrypy.expose
	def index(self, url, quality=None, audio=None, format=None):
		youtube_video=YoutubeEpisode(
			url,
			quality=Noneable(Quality(quality)).value(),
			audio=self.audio,
			format=format,)
		cherrypy.response.headers['Content-Type'] = youtube_video.mimetype()
		return youtube_video.generate()




class Feed(object):
	def __init__(self, yourss_base_url, base_url, clip_base_url, audio=False):
		self.yourss_base_url=yourss_base_url
		self.base_url=base_url
		self.clip_base_url=clip_base_url
		self.audio=audio
	@cherrypy.expose
	def index(self, url, quality='high', format='', page_index=1, page_size=10):
		cherrypy.response.headers['Content-Type']='text/xml'
		try:
			return YoutubeFeed(
				url,
			    yourss_base_url=self.yourss_base_url,
			    base_url=self.base_url,
			    clip_base_url=self.clip_base_url,
			    quality=Quality(quality).value(),
			    audio=self.audio,
			    format=format,
			    page_index=PageIndex(page_index).value(),
			    page_size=PageSize(page_size).value()
			).generate()
		except ParameterError as e:
			return Response(e.code, e.message)




class Yourss(Router):
	def __init__(self, yourss_base_url, base_url):
		self.yourss_base_url=yourss_base_url
		self.base_url=base_url
		Router.__init__(self,
			Route(('feed', 'video'), Feed(
					yourss_base_url=self.yourss_base_url,
					base_url=UrlText(self.base_url, 'feed', 'video').text(),
					clip_base_url=UrlText(self.base_url, 'video').text())),
			Route(('feed', 'audio'), Feed(
					yourss_base_url=self.yourss_base_url,
					base_url=UrlText(self.base_url, 'feed', 'audio').text(),
					clip_base_url=UrlText(self.base_url, 'audio').text()))
		)
	@cherrypy.expose
	def index(self, url=None,
	          youtube=None, user=None, channel=None, playlist=None,
	          feed=True, links='direct', episode=False, audio=False, video=True,
	          page_index=1, page_size=10,
	          match_title = None, ignore_title = None,
	          quality='high', format=None):



		pass



class Root(Router):
	def __init__(self, base_url):
		self.base_url=base_url
		parts=('api', 'v1')
		Router.__init__(self, Route(parts, Yourss(self.base_url, base_url=UrlText(self.base_url, *parts).text())))
	@cherrypy.expose
	def index(self):
		return PystacheArtifact('index.mustache', {'base_url': self.base_url}).text()