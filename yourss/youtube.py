import youtube_dl
import json
from .text import PypathTextFile, Text, UrlQuery, PystacheArtifact
from .async import generate_stdout
from functools import reduce
from pystache import render







class YoutubeEpisodePageUrl(Text):
	"""from youtube id to full url"""
	def __init__(self, id):
		self.id=id
	def text(self):
		return 'https://www.youtube.com/watch?v=' + self.id
	def __str__(self):
		return self.text()



class YoutubeResource(object):
	def __init__(self, url, yourss_base_url, base_url, clip_base_url, quality='high', audio=False, format=None):
		self.url=url
		self.yourss_base_url=yourss_base_url
		self.base_url=base_url
		self.clip_base_url=clip_base_url
		self.quality=quality
		self.audio=audio
		self.format=format
	def get_ydl_format(self):
		if self.format:
			return format
		elif not self.audio:
			if self.quality=='low':
				return 'worst[ext=mp4]'
			else:
				return 'best[ext=mp4]'
		else:
			if self.quality=='low':
				return 'worstaudio'
			else:
				return 'bestaudio'



class YdlFormat(Text):
	def __init__(self, quality=None, audio=False, format=None):
		self.quality=quality
		self.audio=audio
		self.format=format
	def text(self):
		if self.format:
			return self.format
		elif not self.audio:
			if self.quality=='low':
				return 'worst[ext=mp4]/worst'
			else:
				return 'best[ext=mp4]/best'
		else:
			if self.quality=='low':
				return 'worstaudio'
			else:
				return 'bestaudio'


class YourssUrlText(Text):
	def __init__(self, base_url, url, quality=None, audio=False, format=None):
		self.base_url=base_url
		self.url=url
		self.quality=quality
		self.audio=audio
		self.format=format
	def text(self):
		param_dic={'url': self.url}
		if self.format: param_dic['format']=self.format
		elif self.quality!='high': param_dic['quality']=self.quality
		return self.base_url + UrlQuery(**param_dic).text()



class YourssUrlParams(object):
	def __init__(self, quality='high', audio=False, format=None):
		self.quality=quality
		self.audio=audio
		self.format=format
	def as_dict(self):
		result={}
		if self.format: result['format']=self.format
		else:
			if self.audio: result['audio']=True
			if self.quality!='high': result['quality']=self.quality
		return result



class Feed(object):
	def __init__(self, url, yourss_base_url, base_url, clip_base_url, quality='high', audio=False, format=None, start_index=1, end_index=10):
		self.url=url
		self.yourss_base_url=yourss_base_url
		self.base_url=base_url
		self.clip_base_url=clip_base_url
		self.quality=quality
		self.audio=audio
		self.format=format
		self.start_index=start_index
		self.end_index=end_index
	def get_ydl_opts(self):
		return {'noplaylist': False, 'forcejson': True, 'skip_download': True, 'playliststart': self.start_index, 'playlistend': self.end_index, 'format': YdlFormat(self.quality, self.audio, self.format).text()}
	def _action(self):
		with youtube_dl.YoutubeDL(self.get_ydl_opts()) as ydl:
			ydl.download([self.url])
	def get(self):
		return reduce(lambda a, b: a+b, self.generate())
	def generate(self):
		aux_params=YourssUrlParams(self.quality, self.audio, self.format)

		feed_query={'url': self.url}
		feed_query.update(aux_params.as_dict())

		feed_data={
			'url': self.url,
			'date': 'now time',
			'yourss_url': self.yourss_base_url,
			'yourss_feed_url': YourssUrlText(self.base_url, self.url, self.quality, self.audio, self.format).text()
		}
		yield PystacheArtifact('rss-header.mustache', feed_data).text()
		for line in generate_stdout(self._action):
			if not line.startswith('{'): continue
			item = json.loads(line)
			if not item['url']:
				if item['webpage_url']:
					pass
				elif 'Youtube' == item.get('extractor_key', None) or 'Youtube' == item.get('ie_key', None):
					item['webpage_url']=YoutubeEpisodePageUrl(item['id'])
				else:
					continue
				item['url']=YourssUrlText(self.clip_base_url, item['web_page_url'], self.quality, self.audio, self.format).text()
			item['mimetype']='audio/' + item['ext'] if self.audio else 'video/' + item['ext']
			item['yourss_url']=self.base_url
			if item['tags']:
				item['tag_str']=','.join(item['tags'])
			if not item.get('filesize', None):
				for format in item.get('formats', ()):
					if format['format_id'] == item['format_id']:
						item['filesize'] = format.get('filesize', None)
			yield PystacheArtifact('rss-item.mustache', item).text()
		yield PystacheArtifact('rss-footer.mustache', feed_data).text()




class Episode(object):
	def __init__(self, url, quality='high', audio=False, format=None):
		self.url=url
		self.quality=quality
		self.audio=audio
		self.format=format
		self.ydl_format=YdlFormat(self.quality, self.audio, self.format).text()
	def _action_info(self):
		ydl_opts = {'noplaylist': True, 'forcejson': True, 'skip_download': True, 'format': self.ydl_format}
		with youtube_dl.YoutubeDL(ydl_opts) as ydl:
			ydl.download([self.url])
	def _action_download(self):
		ydl_opts = {'noplaylist': False, 'outtmpl': '-', 'quiet': True, 'format': self.ydl_format}
		with youtube_dl.YoutubeDL(ydl_opts) as ydl:
			ydl.download([self.url])
	def mimetype(self):
		for line in generate_stdout(self._action_info):
			if not line.startswith('{'): continue
			j = json.loads(line)
			return 'audio/' + j['ext'] if self.audio else 'video/' + j['ext']
		return 'audio/webm' if self.audio else 'video/mp4'
	def generate(self):
		def generator():
			for line in generate_stdout(self._action_download):
				yield line
		return generator()