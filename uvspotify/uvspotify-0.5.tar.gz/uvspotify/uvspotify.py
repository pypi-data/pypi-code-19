from uvoauth.uvoauth import Oauth

class SpotifyScopes:
    PLAYLIST_READ_PRIVATE = 'playlist-read-private'
    PLAYLIST_READ_COLLABORATIVE = 'playlist-read-private'
    PLAYLIST_MODIFY_PUBLIC = 'playlist-modify-public'
    PLAYLIST_MODIFY_PRIVATE = 'playlist-modify-private'
    STREAMING = 'streaming'
    UGC_IMAGE_UPLOAD = 'ugc-image-upload'
    USER_FOLLOW_MODIFY = 'user-follow-modify'
    USER_FOLLOW_READ = 'user-follow-read'
    USER_LIBRARY_READ = 'user-library-read'
    USER_LIBRARY_MODIFY = 'user-library-modify'
    USER_READ_PRIVATE = 'user-read-private'
    USER_READ_BIRTHDATE = 'user-read-birthdate'
    USER_READ_EMAIL = 'user-read-email'
    USER_TOP_READ = 'user-top-read'
    USER_READ_PLAYBACK_STATE = 'user-read-playback-state'

class Spotify(Oauth):
    """
    Spotify client for :mod:`uvhttp`.
    """
    def __init__(self, loop, client_id, client_secret, redirect_url,
            **kwargs):
        self.spotify_oauth = 'https://accounts.spotify.com/'
        self.spotify_api = b'https://api.spotify.com/v1'

        super().__init__(loop, self.spotify_oauth + 'authorize',
            self.spotify_oauth + 'api/token', client_id, client_secret,
            redirect_url=redirect_url, **kwargs)

    async def api(self, method, path, *args, **kwargs):
        """
        Make an API request to spotify with the given path.

        The path should be everything except for the common part of the URL.

        For example, ``https://api.spotify.com/v1/me/player/devices`` becomes
        ``/me/player/devices``.
        """

        return await self.request(method, self.spotify_api + path, *args, **kwargs)
