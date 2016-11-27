import cherrypy
from .youtube import YoutubeRss
from .youtube import YoutubeVideo
from .text import UrlText



def Response(code, message):
	cherrypy.response.status = code
	return message




class Video(object):
	def __init__(self, yourss_base_url, base_url):
		self.yourss_base_url=yourss_base_url
	@cherrypy.expose
	def index(self, url, quality=None, audio=None, format=None):
		if not quality in ['high', 'low', None]:
			return Response(400, 'quality should either high (default) or low')
		if not audio in ['true', 'false', None]:
			return Response(400, 'audio should either true or false (default)')
		audio=True if 'true'==audio else False
		youtube_video=YoutubeVideo(url, quality=quality, audio=audio, format=format)
		cherrypy.response.headers['Content-Type'] = youtube_video.mimetype()
		return youtube_video.data()




class Feed(object):
	def __init__(self, yourss_base_url, base_url, clip_base_url):
		self.yourss_base_url=yourss_base_url
		self.base_url=base_url
		self.clip_base_url=clip_base_url
	@cherrypy.expose
	def index(self, url, quality='high', audio='false', format='', start_index=1, end_index=10):
		if not quality in ['high', 'low', None]:
			return Response(400, 'quality should either high (default) or low')
		if not audio in ['true', 'false', None]:
			return Response(400, 'audio should either true or false (default)')
		audio=True if 'true'==audio else False
		cherrypy.response.headers['Content-Type']='text/xml'
		return YoutubeRss(url, yourss_base_url=self.yourss_base_url, base_url=self.base_url, clip_base_url=self.clip_base_url, quality=quality, audio=audio, format=format).get()



class Router(object):
	def __init__(self, routes):
		self.routes=routes
	def _cp_dispatch(self, vpath):
		if len(vpath) > 0:
			for item in self.routes:
				if   isinstance(item[0], str):           pattern = (item[0],)
				elif isinstance(item[0], (list, tuple)): pattern = item[0]
				else:                                    raise 'wrong type'
				if len(vpath)<len(pattern): continue
				if '/'.join(vpath[:len(pattern)]) == '/'.join(pattern):
					for i in range(len(pattern)): vpath.pop(0)
					return item[1]
		else:
			route=self.routes.get('', None)
			return route
		return vpath




class Yourss(Router):
	def __init__(self, yourss_base_url, base_url):
		self.yourss_base_url=yourss_base_url
		self.base_url=base_url
		Router.__init__(self, [
			('video', Video(self.yourss_base_url, UrlText(self.base_url, 'video').text())),
			('feed',  Feed(self.yourss_base_url, UrlText(self.base_url, 'feed').text(), UrlText(self.base_url, 'video').text())),
		])




class Root(Router):
	def __init__(self, base_url):
		self.base_url=base_url
		parts=('api', 'v1')
		Router.__init__(self, [
			(parts, Yourss(self.base_url, UrlText(self.base_url, *parts).text()))
		])
	@cherrypy.expose
	def index(self):
		from os.path import dirname, abspath, join
		return open(join(dirname(abspath(__file__)), 'index.html')).readlines()