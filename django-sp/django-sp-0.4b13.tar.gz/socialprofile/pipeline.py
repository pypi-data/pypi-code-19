"""Python Social Auth Pipeline Extensions"""

from social_core.backends.google import GoogleOAuth2 as GoogleOAuth2
from social_core.backends.twitter import TwitterOAuth as TwitterOAuth
from social_core.backends.facebook import FacebookOAuth2 as FacebookOAuth2

def create_profile(user, is_new=False, *args, **kwargs):
    """Create a profile instance for the given user"""
    if is_new:
        profile = user.get_profile()
        if profile is None:
            profile = Profile(user_id=user.id)
        profile.gender = response.get('gender')
        profile.link = response.get('link')
        profile.timezone = response.get('timezone')
        profile.save()

def socialprofile_extra_values(backend, details, response, uid, user, *args, **kwargs):
    """Routes the extra values call to the appropriate back end"""
    if type(backend) is GoogleOAuth2:
        return {'user': google_extra_values(backend, details, response, uid, user, *args, **kwargs) }

    if type(backend) is TwitterOAuth:
        return {'user': twitter_extra_values(backend, details, response, uid, user, *args, **kwargs) }

    if type(backend) is FacebookOAuth2:
        return {'user': facebook_extra_values(backend, details, response, uid, user, *args, **kwargs) }

def google_extra_values(backend, details, response, uid, user, *args, **kwargs):
    """Populates a UserProfile Object when a new User is created via Google Auth"""
    if not user.manually_edited:
        user.last_name = response.get('name').get('familyName', '')
        user.first_name = response.get('name').get('givenName', '')
        user.save()

        user.gender = response.get('gender', '')
        user.image_url = response.get('image').get('url', '')
        user.google_isPlusUser = response.get('isPlusUser', False)
        user.google_plusUrl = response.get('url', '')
        user.google_circledByCount = response.get('circledByCount', 0)
        user.google_language = response.get('language', '')
        user.google_kind = response.get('kind', '')
        user.google_verified = response.get('verified', False)
		
        user.editByGoogle = True
        user.save()
        return user
    return response
	
def facebook_extra_values(backend, details, response, uid, user, *args, **kwargs):
    """Populates a UserProfile Object when a new User is created via Facebook Auth"""
    if not user.manually_edited:
        user.last_name = response.get('last_name', '')
        user.first_name = response.get('first_name', '')
        user.save()

        user.gender = response.get('gender', '')
        user.url = response.get('link', '')
        if response.get('picture', False):
            user.image_url = response.get('picture').get('data').get('url', '')

        user.save()
        return user
    return response

def twitter_extra_values(backend, details, response, uid, user, *args, **kwargs):
    """Populates a UserProfile Object when a new User is created via Twitter Auth"""
    if not user.manually_edited:
        try:
            first_name, last_name = response.get('name', '').split(' ', 1)
        except:
            first_name = response.get('name', '')
            last_name = ''
        user.last_name = last_name
        user.first_name = first_name
        user.save()

        user.url = response.get('url', '')
        user.image_url = response.get('profile_image_url_https', '')
        user.description = response.get('description', '')

        user.save()
        return user
    return response