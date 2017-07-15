
import api


class Comment:

	def __init__(self, meta):
		self.setup_meta(meta)

	def setup_meta(self, meta):
		from User import User
		
		if meta:
			self.meta = meta

			for key, value in meta.items():
				if key == 'user':
					value = User(meta={'user': value})
				if key == 'comments':
					value = [
						Comment(comment) for comment in value
					]

				# Add item to class
				setattr(self, key, value)
				# Add getter for item
				setattr(self, 'get_' + key, lambda k=key: self._get_safe(k))

	def get_user(self):
		return False

	def get_viewerVote(self):
		return False

	def get_comments(self):
		return False

	def _get_safe(self, name):
		if hasattr(self, name):
			return getattr(self, name)
		else:
			return False

	def _api_call(self, session, action, args = {}):
		comment_id = self._get_safe('comment_id')

		args['session'] = session

		if comment_id:
			video_action = api.request('/comment/' + comment_id + '/' + action, data=args)

			if video_action:
				self.set_meta(video_action)
				return True
			else:
				return False
		return False

	def vote(self, session, vote = True):
		if vote:
			vote = 1
		else:
			vote = 0

		return self._api_call(session, 'vote', dict(value=vote))

	def vote(self, session):
		return self._api_call(session, 'delete')
