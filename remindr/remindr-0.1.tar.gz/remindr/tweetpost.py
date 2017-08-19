# vim:ts=4:sw=4:ft=python:fileencoding=utf-8
# Copyright © 2017 Carl Chenet <carl.chenet@ohmytux.com>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

'''Post a tweet to Twitter'''

# standard libraires imports
import logging

# 3rd party libraries imports
import feedparser
import tweepy

def tweetpost(clioptions, cfgoptions, tweet, language):
    '''Post a tweet'''
    if clioptions.dryrun:
         print('Should have tweeted => {tweet}'.format(visibility=cfgoptions['mastodon_toot_visibility'], tweet=tweet))
    else:
        consumer_key = cfgoptions['twitter_consumer_key']
        consumer_secret = cfgoptions['twitter_consumer_secret']
        access_token = cfgoptions['twitter_access_token']
        access_token_secret = cfgoptions['twitter_access_token_secret']
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth)
        try:
            if 'path_to_image' in cfgoptions:
                api.update_with_media(cfgoptions['path_to_image'], tweet)
            elif '{lang}_image_path'.format(lang=language) in cfgoptions:
                api.update_with_media(cfgoptions['{lang}_image_path'.format(lang=language)], tweet)
            # if the user uses mastodon_image_path
            elif 'twitter_image_path' in cfgoptions:
                api.update_with_media(cfgoptions['twitter_image_path'], tweet)
            # if the user users {lang}_image_path
            elif 'twitter_{lang}_image_path'.format(lang=language) in cfgoptions:
                api.update_with_media(cfgoptions['twitter_{lang}_image_path'.format(lang=language)], tweet)
            else:
                api.update_status(tweet)
        except tweepy.TweepError as err:
            logging.warning('Error occurred while updating status: {err}'.format(err=err))
