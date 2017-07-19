import pandas as pd
from transcend.services.data_service import DataService

class Twitter(DataService):
    def __init__(self, parent, raw_data, name="twitter"):
        super(self.__class__, self).__init__(parent, raw_data, name)

    def people_you_like_most(self, MOST_COMMON=35):
        '''
            RETURNS

            [{
                'username' : 'mikeyf76' ,
                'likeCount' : 2017
            },
            ...]

        '''
        likes = self.raw_data['favorites']
        liked = map(lambda x : x['user']['screen_name'], likes)
        liked_counts = Counter(liked)
        formatted = map(lambda x: {'username': x[0], 'likeCount': x[1]}, liked_counts.most_common(MOST_COMMON))
        return formatted
