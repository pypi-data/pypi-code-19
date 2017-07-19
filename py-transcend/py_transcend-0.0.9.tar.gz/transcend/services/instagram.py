import pandas as pd
import numpy as np
from transcend.services.data_service import DataService

from collections import Counter


class Instagram(DataService):
    '''
        Object to manipulate instagram data
    '''
    def __init__(self, parent, raw_data, name="instagram"):
        super(self.__class__, self).__init__(parent, raw_data, name)

    def posts_thru_time(self):
        '''
            Analytics for each post, typically can just create a function
            that takes in a post json object and updates the post to include 
            a new analytic

            RETURNS

            [{
                'avgComments': 2.3461538461538463,
                'avgLikes': 32.019230769230766,
                'commentsCount' : 72 ,
                'likesCount' : 2004,
                'timestamp' : datetime.datetime(2017, 1, 17, 21, 54, 19, 792000),
                'likesFollwerRatio' :
            },
            ...]

        '''
        def add_likes_follower_ratio(post, follow_count_ts):
            ts = post['timestamp']
            data_before = filter(lambda x: x[0] <= ts, follow_count_ts)

            if len(data_before) == 0:
                post['likesFollwerRatio'] = None
            else:
                followers = max(data_before, key=lambda x: x[0])[1]
                if followers > 0:
                    likes = float(post['likesCount'])
                    post['likesFollwerRatio'] = likes / followers
                else:
                    post['likesFollwerRatio'] = None
            return post

        def add_likes_comments_ra(post):
            earlier_posts = filter(lambda x: x['timestamp'] < post['timestamp'], posts)

            if len(earlier_posts) > 0:
                avg_likes = round(np.mean(map(lambda x: x['likesCount'], earlier_posts)), 3)
                avg_comments = round(np.mean(map(lambda x: x['commentsCount'], earlier_posts)), 3)
                post['avgComments'] = avg_comments
                post['avgLikes'] = avg_likes
            else:
                post['avgComments'] = None
                post['avgLikes'] = None

            return post

        posts = self.raw_data['posts']
        data = self.raw_data['data']
        follow_count_ts = map(lambda x: (x['timestamp'], x['followingCount']), data)
        formatted = map(lambda x: {
                            'commentsCount': x['commentsCount'],
                            'likesCount': x['likesCount'],
                            'timestamp': x['timestamp'],
                        },
                        posts)
        formatted = map(lambda x: add_likes_follower_ratio(x, follow_count_ts), formatted)
        formatted = list(map(lambda x: add_likes_comments_ra(x), formatted))

        return formatted

    def people_you_like_most(self, MOST_COMMON=35):
        '''
            RETURNS

            [{
                'username' : 'mikeyf76' ,
                'likeCount' : 2017
            },
            ...]

        '''
        likes = self.raw_data['likes']
        liked = map(lambda x: x['postedBy'], likes)
        liked_counts = Counter(liked)
        formatted = list(map(lambda x: {'username': x[0], 'likeCount': x[1]}, liked_counts.most_common(MOST_COMMON)))
        return formatted

    def people_youre_tagged_with(self, MOST_COMMON=35):
        '''
            RETURNS

            [{
                'username' : 'mikeyf76' ,
                'tagCount' : 7
            },
            ...]

        '''
        posts = self.raw_data['posts']
        tags_per_post = map(lambda x: map(lambda y: y['username'], x['usersTagged']), posts)
        all_tags = reduce(lambda x: x[0]+x[1], tags_per_post, [])
        top_tags = Counter(all_tags).most_common(MOST_COMMON)
        formatted = list(map(lambda x: {'username': x[0], 'tagCount': x[1]}, top_tags))
        return formatted

    def top_geolocations(self, MOST_COMMON=35):
        '''
            RETURNS

            [{
                'latitude' : 35.234234 ,
                'longitude' : 24.234234,
                'name' : 'Boston',
                'locCount' : 3
            },
            ...]

        '''
        posts = self.raw_data['posts']
        locations = map(lambda x: x['location'], filter(lambda x: 'location' in x, posts))
        # locations = map(lambda x : {'latitude': x['latitude'], 'longitude' : x['longitude'], 'name' : x['name']}, locations)
        key = map(lambda x: frozenset(x.items()), locations)
        top_locations = Counter(key).most_common(15)
        top_locations = map(lambda x: (dict(x[0]), x[1]), top_locations)
        formatted = map(lambda x: {'latitude': x[0]['latitude'] if 'latitude' in x[0] else None, 
                                        'longitude': x[0]['longitude'] if 'longitude' in x[0] else None, 
                                        'name': x[0]['name'] if 'name' in x[0] else None, 
                                        'locCount': x[1]}, top_locations)
        return list(formatted)

    def follow_history_thru_time(self):
        '''
            RETURNS

            [{
                'followerCount' : 430 ,
                'followingCount' : 511,
                'followerFollowingRatio' : 0.841,
                'timestamp': datetime.datetime(2017, 1, 17, 21, 54, 19, 792000)
            },
            ...]

        '''
        data = self.raw_data['data']

        def get_ratio(timepoint):
            followers = timepoint['followerCount']
            following = timepoint['followingCount']
            ratio = None
            if following > 0:
                ratio = round(float(followers) / following, 3)
            timepoint['followerFollowingRatio'] = ratio
            return timepoint

        following_followers_ratio = map(get_ratio, data)
        formatted = map(lambda x: {'followerCount': x['followerCount'],
                                   'followingCount': x['followingCount'],
                                   'timestamp': x['timestamp'],
                                   'followerFollowingRatio': x['followerFollowingRatio']}, data)
        return list(formatted)

    def top_filters(self, MOST_COMMON=35):
        '''
            RETURNS

            [{
                'filter' : 'Lo-fi' ,
                'filtCount': 17
            },
            ...]

        '''
        posts = self.raw_data['posts']
        filters = map(lambda x: x['_filter'] if '_filter' in x else None, posts)
        top_filters = Counter(filters).most_common(15)
        formatted = map(lambda x: {'filter': x[0], 'filtCount': x[1]}, top_filters)
        return list(formatted)
