import youtube_dl
import json
from .text import Text, UrlQuery, PystacheArtifact, UrlText, PystacheFileTemplate
from .asynch import StdoutRedirector
from functools import reduce
from datetime import datetime
import logging
from .valid import default_feed_parameter_values

class YoutubeVideoPageUrl(Text):
	"""from youtube id to full url"""
	def __init__(self, iD):
		self._id=iD
	def text(self):
		return 'https://www.youtube.com/watch?v=' + self._id
	def __str__(self):
		return self.text()

class YdlFormat(Text):
	def __init__(self, media_type='video', quality='high', format=None):
		self.media_type=media_type
		self.quality=quality
		self.format=format
	def text(self):
		if self.format: return self.format
		elif 'video'==self.media_type: return 'worst[ext=mp4]/worst' if self.quality=='low' else 'best[ext=mp4]/best'
		else:                          return 'worstaudio/worst'     if self.quality=='low' else 'bestaudio/best'


class FeedLink(Text):
	def __init__(self, base_url, url,
	             match_title=None, ignore_title=None, page_index=1, page_size=10,
	             media_type='video', quality='high', format=None, link_type='direct',
	             title=None, thumbnail=None):
		self._base_url=base_url
		self._url=url
		self._match_title=match_title
		self._ignore_title=ignore_title
		self._page_index=page_index
		self._page_size=page_size
		self._media_type = media_type
		self._quality = quality
		self._format = format
		self._link_type=link_type
		self._title=title
		self._thumbnail=thumbnail
	def text(self):
		param_dic={'url': self._url, 'match_title': self._match_title, 'ignore_title': self._ignore_title,
				   'title': self._title, 'thumbnail': self._thumbnail}
		if self._page_index != default_feed_parameter_values['page_index']: param_dic['page_index']=self._page_index
		if self._page_size  != default_feed_parameter_values['page_size']: param_dic['page_size']=self._page_size
		if self._link_type  != default_feed_parameter_values['link_type']: param_dic['link_type']=self._link_type
		param_dic.update(YourssFormatUrlParams(self._media_type, self._quality, self._format).as_dict())
		return self._base_url + UrlQuery(**param_dic).text()



class YourssFormatUrlParams(object):
	def __init__(self, media_type='video', quality='high', format=None):
		self._media_type=media_type
		self._quality=quality
		self._format=format
	def as_dict(self):
		result={}
		if self._format:
			result['format']=self._format
		else:
			if self._media_type and self._media_type != default_feed_parameter_values['media_type']:
				result['media_type']=self._media_type
			if self._quality and self._quality  != default_feed_parameter_values['quality']:
				result['quality']=self._quality
		return result


class EpisodeLink(Text):
	def __init__(self, clip_base_url, ydl_json, media_type='video', quality='high', format_=None, link_type='direct'):
		self.clip_base_url=clip_base_url
		self.ydl_json=ydl_json
		self.media_type=media_type
		self.quality=quality
		self.format=format_
		self.link_type=link_type
	def webpage_url(self):
		if 'webpage_url' in self.ydl_json:
			return self.ydl_json['webpage_url']
		elif 'Youtube' == self.ydl_json.get('extractor_key', None) or 'Youtube' == self.ydl_json.get('ie_key', None):
			return YoutubeVideoPageUrl(self.ydl_json['id']).text()
		else: raise Exception('cannot extract webpage url from youtube_dl output')
	def direct_url(self):
		return self.ydl_json['url']
	def proxy_url(self):
		url_data={'url': self.webpage_url()}
		url_data.update(YourssFormatUrlParams(self.media_type, self.quality, self.format).as_dict())
		return UrlText(self.clip_base_url, UrlQuery(**url_data))
	def text(self):
		return {'webpage': self.webpage_url, 'direct': self.direct_url, 'proxy': self.proxy_url}[self.link_type]()


class DateRfc822D(Text):
	def __init__(self, value):
		self._value=value
	def text(self):
		if not self._value: return None
		date = self._value if isinstance(self._value, datetime) else datetime.strptime(self._value, '%Y%m%d')
		return date.strftime('%a, %d %b %Y %H:%M:%S %Z')

class YdlFileSize(object):
	def __init__(self, j):
		self.j=j
	def value(self):
		if self.j.get('filesize', None):
			return self.j['filesize']
		else:
			for format_ in self.j.get('formats', ()):
				if format_['format_id'] == self.j['format_id']:
					return format_.get('filesize', None)




class Feed(object):
	def __init__(self, url,
				 match_title=None, ignore_title=None, page_index=1, page_size=10,
				 media_type='video', quality='high', format=None, link_type='direct',
				 title=None, thumbnail=None,
				 yourss_base_url=None, feed_base_url=None, episode_base_url=None):
		self.url=url
		self.match_title=match_title
		self.ignore_title=ignore_title
		self.page_index=page_index
		self.page_size=page_size
		self.media_type=media_type
		self.quality=quality
		self.format=format
		self.link_type=link_type
		self.title=title
		self.thumbnail=thumbnail
		self.yourss_base_url = yourss_base_url
		self.feed_base_url = feed_base_url
		self.episode_base_url = episode_base_url
	def get_ydl_opts(self):
		return { 'noplaylist': False, 'forcejson': True, 'skip_download': True,
		         'matchtitle': self.match_title, 'rejecttitle': self.ignore_title, 'ignoreerrors': True,
		         'playliststart': (self.page_index-1)*self.page_size+1, 'playlistend': self.page_index*self.page_size,
		         'format': YdlFormat(self.media_type, self.quality, self.format).text() }

	def _action(self):
		with youtube_dl.YoutubeDL(self.get_ydl_opts()) as ydl:
			ydl.download([self.url])

	def get(self):
		return reduce(lambda a, b: a+b, self.generate())

	def generate(self):
		once_flag=True
		feed_data = {
			'url': self.url,
			'date': DateRfc822D(datetime.now()),
			'yourss_base_url': self.yourss_base_url,
			'feed_url': FeedLink(self.feed_base_url, self.url, self.match_title, self.ignore_title,
								 self.page_index, self.page_size,
								 self.media_type, self.quality, self.format,
								 self.link_type, self.title, self.thumbnail).text(),
			'thumbnail': self.thumbnail,
			'title': None
		}
		for line in StdoutRedirector(self._action):
			if not line.startswith('{'): continue
			item = json.loads(line)

			# generate header
			if once_flag:
				once_flag=False
				feed_data['title']=self.title if self.title else item['playlist_title'] if 'playlist_title' in item else 'Episodes from ' + self.url
				yield PystacheArtifact(PystacheFileTemplate('rss-header'), **feed_data).text()
			try:
				item['url']=EpisodeLink(self.episode_base_url, item, self.media_type, self.quality, self.format, self.link_type).text()
			except Exception as e:
				logging.getLogger(__name__).error('unable to generate url', e)
				continue
			item['upload_date']=DateRfc822D(item.get('upload_date')).text()
			item['mimetype']='audio/' + item.get('ext', 'webm') if self.media_type=='audio' else 'video/' + item.get('ext', 'mp4')
			item['yourss_url']=self.yourss_base_url
			if 'tags' in  item:
				item['tag_str']=','.join(item['tags'])
			item['filesize']=YdlFileSize(item).value()
			yield PystacheArtifact(PystacheFileTemplate('rss-item'), **item).text()
		if once_flag:
			if not feed_data['title']:
				feed_data['title']=self.title if self.title else 'Episodes from ' + self.url
			yield PystacheArtifact(PystacheFileTemplate('rss-header'), **feed_data).text()
		yield PystacheArtifact(PystacheFileTemplate('rss-footer'), **feed_data).text()




class Episode(object):
	def __init__(self, url, media_type='audio', quality='low', format=None):
		self.url=url
		self.media_type=media_type
		self.quality=quality
		self.format=format
		self.ydl_format=YdlFormat(media_type, quality, format).text()
		self.j=None
	def _action_info(self):
		ydl_opts = {'noplaylist': True, 'forcejson': True, 'skip_download': True, 'format': self.ydl_format}
		with youtube_dl.YoutubeDL(ydl_opts) as ydl:
			ydl.download([self.url])
	def _action_download(self):
		ydl_opts = {'noplaylist': False, 'outtmpl': '-', 'quiet': True, 'format': self.ydl_format}
		with youtube_dl.YoutubeDL(ydl_opts) as ydl:
			ydl.download([self.url])
	def get_info(self):
		if not self.j:
			self.j={}
			for line in StdoutRedirector(self._action_info):  # StdoutRedirector must be disposed
				if not line.startswith('{'): continue
				self.j=json.loads(line)
		return self.j
	def get_ext(self):
		return self.get_info().get('ext', 'webm') if self.media_type=='audio' else self.get_info().get('ext', 'mp4')
	def mimetype(self):
		j=self.get_info()
		if j: return 'audio/' + self.get_ext() if 'audio' == self.media_type else 'video/' + self.get_ext()
		else: return 'application/octet-stream'
	def filesize(self):
		j=self.get_info()
		if j: return YdlFileSize(j).value()
		else: return None
	def filename(self):
		#return hashlib.sha224(self.url.encode('UTF-8')).hexdigest() + '.' + self.get_ext()
		return (self.get_info()['id'] if 'id' in self.get_info() else 'episode') + '.' + self.get_ext()
	def thumbnail(self):
		return self.get_info().get('thumbnail', None)
	def generate(self):
		def generator():
			for line in StdoutRedirector(self._action_download):
				yield line
		return generator()