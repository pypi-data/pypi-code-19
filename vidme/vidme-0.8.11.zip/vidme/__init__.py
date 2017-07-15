
from Session import Session
from Video import Video
from Comment import Comment
from User import User
from Album import Album

def _get_videos(videos_type, **kwargs):
	videos = api.request('/videos/' + videos_type, method="GET", params=kwargs)

	if videos and 'videos' in videos:
		return [
			Video(meta={'video': video})
			for video in videos['videos']
		]
	else:
		return False

def get_featured(**kwargs):
	# offset (int)
	# limit (int)
	# marker (string)
	# order (string)
	return _get_videos('featured', **kwargs)

def get_hot(**kwargs):
	# subindex (int)
	# offset (int)
	# limit (int)
	return _get_videos('hot', **kwargs)

def get_new(**kwargs):
	# nsfw (1 for true, 0 for false)
	return _get_videos('new', **kwargs)

def get_trending(**kwargs):
	# offset (int)
	# limit (int)
	return _get_videos('trending', **kwargs)

def get_search(query = "", **kwargs):
	# nsfw (1 for true, 0 for false)
	# order (string :: 'likes_count', 'hot_score', 'date_completed')
	# user (string)
	kwargs['query'] = query
	return _get_videos('search', **kwargs)
