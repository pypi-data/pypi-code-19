BASE_URL = 'https://www.instagram.com/'
LOGIN_URL = BASE_URL + 'accounts/login/ajax/'
LOGOUT_URL = BASE_URL + 'accounts/logout/'
MEDIA_URL = BASE_URL + '{0}/media'

STORIES_URL = 'https://i.instagram.com/api/v1/feed/user/{0}/reel_media/'
STORIES_UA = 'Instagram 9.5.2 (iPhone7,2; iPhone OS 9_3_3; en_US; en-US; scale=2.00; 750x1334) AppleWebKit/420+'
STORIES_COOKIE = 'ds_user_id={0}; sessionid={1};'

TAGS_URL = BASE_URL + 'explore/tags/{0}/?__a=1'
LOCATIONS_URL = BASE_URL + 'explore/locations/{0}/?__a=1'
VIEW_MEDIA_URL = BASE_URL + 'p/{0}/?__a=1'
SEARCH_URL = BASE_URL + 'web/search/topsearch/?context=blended&query={0}'

QUERY_COMMENTS = BASE_URL + 'graphql/query/?query_id=17852405266163336&shortcode={0}&first=100&after={1}'
QUERY_HASHTAG = BASE_URL + 'graphql/query/?query_id=17882293912014529&tag_name={0}&first=100&after={1}'
QUERY_LOCATION = BASE_URL + 'graphql/query/?query_id=17881432870018455&id={0}&first=100&after={1}'
