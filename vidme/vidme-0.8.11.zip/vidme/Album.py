
import api

class Album:

	def __init__(self, album_id = "", meta = ""):
		self.album_id = album_id

		if meta:
			self.set_meta(meta)
		elif album_id:
			self.set_meta(self.retrieve_meta())

		self.videos = []

	def retrieve_meta(self):
		album = False

		if self.album_id:
			album = api.request('/album/' + str(self.album_id), method="GET")

		return album

	def set_meta(self, meta):
		# Confirm meta is good
		self.meta = meta

		if 'album' in meta:
			album = meta['album']

			for key, value in album.items():
				# Add item to class
				setattr(self, key, value)
				# Add getter for item
				setattr(self, 'get_' + key, lambda k=key: self._get_safe(k))

	def _retrieve_videos(self, limit=20, offset=0, session=None, order=None, private=0):
		from Video import Video
		
		album_id = self._get_safe('album_id')

		if album_id:
			videos = api.request('/album/' + album_id + '/videos', method="GET", params=dict(
					private=private,
					order=order,
					session=session,
					offset=offset,
					limit=limit,
					album=album_id
				))

			if videos:
				return [
					Video(meta={'video': video}) for video in videos['videos']
				]
			else:
				return False
		else:
			return False

	def _yield_videos(self, limit, offset, session=None, order=None, private=0):
		self.videos = []

		while True:
			videos = self._retrieve_videos(limit, offset, session, order, private)
			if videos and len(videos) > 0:
				self.videos.extend(videos)
				offset += limit
				yield videos

				if len(videos) < limit:
					break
			else:
				break

	def get_videos(self, refresh=False, limit=15, offset=0, session=None, order="video_id", private=0):
		videos = self._get_safe('videos')

		# If videos not found, try to retrieve them.
		if refresh or not videos:
			return self._yield_videos(limit, offset)

		videos = self._get_safe('videos')

		if videos:
			return videos
		else:
			return False

	def _get_safe(self, name):
		if hasattr(self, name):
			return getattr(self, name)
		else:
			return False

	def _api_call(self, session, action, args = {}):
		album_id = self._get_safe('album_id')

		args['session'] = session

		if album_id:
			video_action = api.request('/album/' + album_id + '/' + action, data=args)

			if video_action:
				self.set_meta(video_action)
				return True
			else:
				return False
		return False

	def set_title(self, session, title):
		return self._api_call(session, 'edit', dict(title=title))

	def set_description(self, session, description):
		return self._api_call(session, 'edit', dict(description=description))

	def set_url(self, session, url):
		return self._api_call(session, 'edit', dict(url=url))

	def add_video(self, session, video_id):
		album_id = self._get_safe('album_id')

		if album_id:
			video_action = api.request('/album/' + album_id + '/video/' + video_id, params=dict(
				session=session
			))

			if video_action:
				from Video import Video
				self.videos.append(Video(video_id=video_action['albumVideo']['video_id']))
				return True
			else:
				return False
		return False

	def delete(self, session):
		album_id = self._get_safe('album_id')

		if album_id:
			video_action = api.request('/album/' + album_id, params=dict(
				session=session
			), method='DELETE')

			if video_action:
				return True
			else:
				return False
		return False

	def create(self, session, title, description = "", url = ""):
		video_action = api.request('/album', data=dict(
			title=title,
			description=description,
			url=url,
			session=session
		))

		if video_action:
			self.set_meta(video_action)
			return True
		else:
			return False
