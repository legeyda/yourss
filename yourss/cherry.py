import cherrypy
from .youtube import Feed as YoutubeFeed
from .youtube import Episode as YoutubeEpisode
from .text import UrlText, PypathTextFile, PystacheArtifact


def Response(code, message):
	cherrypy.response.status = code
	return message



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



class Validator:
	"""Validator(lambda a: a in ['a', 'b']).check()"""
	def __init__(self, func, message='error', status=400):
		self.func=func
		self.message=message
		self.status=status
	def check(self):
		try:
			if self.func():
				return
		except:
			pass




class Episode(object):
	def __init__(self, yourss_base_url, base_url, audio=False):
		self.yourss_base_url=yourss_base_url
		self.base_url=base_url
		self.audio=audio
	@cherrypy.expose
	def index(self, url, quality=None, audio=None, format=None):
		if not quality in ['high', 'low', None]:
			return Response(400, 'quality should either high (default) or low')
		youtube_video=YoutubeEpisode(url, quality=quality, audio=audio, format=format)
		cherrypy.response.headers['Content-Type'] = youtube_video.mimetype()
		return youtube_video.generate()




class Feed(object):
	def __init__(self, yourss_base_url, base_url, clip_base_url, audio=False):
		self.yourss_base_url=yourss_base_url
		self.base_url=base_url
		self.clip_base_url=clip_base_url
		self.audio=audio
	@cherrypy.expose
	def index(self, url, quality='high', format='', start_index=1, end_index=10):
		if not quality in ['high', 'low', None]:
			return Response(400, 'quality should either high (default) or low')
		try:
			start_index=int(start_index)
			end_index=int(end_index)
		except ValueError:
			return Response(400, 'start_index and end_index should be integers')
		cherrypy.response.headers['Content-Type']='text/xml'
		return YoutubeFeed(url, yourss_base_url=self.yourss_base_url, base_url=self.base_url, clip_base_url=self.clip_base_url, quality=quality, audio=self.audio, format=format, start_index=start_index, end_index=end_index).generate()





class Yourss(Router):
	def __init__(self, yourss_base_url, base_url):
		self.yourss_base_url=yourss_base_url
		self.base_url=base_url
		Router.__init__(self, [
			(
				('feed', 'video'),
				Feed(
					yourss_base_url=self.yourss_base_url,
					base_url=UrlText(self.base_url, 'feed', 'video').text(),
					clip_base_url=UrlText(self.base_url, 'video').text())
			),
			(
				('feed', 'audio'),
				Feed(
					yourss_base_url=self.yourss_base_url,
					base_url=UrlText(self.base_url, 'feed', 'audio').text(),
					clip_base_url=UrlText(self.base_url, 'audio').text())
			),
			('video', Episode(self.yourss_base_url, UrlText(self.base_url, 'video').text())),
			('audio', Episode(self.yourss_base_url, UrlText(self.base_url, 'audio').text())),
		])




class Root(Router):
	def __init__(self, base_url):
		self.base_url=base_url
		parts=('api', 'v1')
		Router.__init__(self, [
			(parts, Yourss(self.base_url, base_url=UrlText(self.base_url, *parts).text()))
		])
	@cherrypy.expose
	def index(self):
		return PystacheArtifact('index.mustache', {'base_url': self.base_url}).text()