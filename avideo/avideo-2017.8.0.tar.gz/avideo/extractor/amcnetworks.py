# coding: utf-8

# Copyright (C) 2017 avideo authors (see AUTHORS)

#
#    This file is part of avideo.
#
#    avideo is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    avideo is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with avideo.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

from .theplatform import ThePlatformIE
from ..utils import (
    int_or_none,
    parse_age_limit,
    try_get,
    update_url_query,
)


class AMCNetworksIE(ThePlatformIE):
    _VALID_URL = r'https?://(?:www\.)?(?:amc|bbcamerica|ifc|wetv)\.com/(?:movies|shows(?:/[^/]+)+)/(?P<id>[^/?#]+)'
    _TESTS = [{
        'url': 'http://www.ifc.com/shows/maron/season-04/episode-01/step-1',
        'md5': '',
        'info_dict': {
            'id': 's3MX01Nl4vPH',
            'ext': 'mp4',
            'title': 'Maron - Season 4 - Step 1',
            'description': 'In denial about his current situation, Marc is reluctantly convinced by his friends to enter rehab. Starring Marc Maron and Constance Zimmer.',
            'age_limit': 17,
            'upload_date': '20160505',
            'timestamp': 1462468831,
            'uploader': 'AMCN',
        },
        'params': {
            # m3u8 download
            'skip_download': True,
        },
        'skip': 'Requires TV provider accounts',
    }, {
        'url': 'http://www.bbcamerica.com/shows/the-hunt/full-episodes/season-1/episode-01-the-hardest-challenge',
        'only_matching': True,
    }, {
        'url': 'http://www.amc.com/shows/preacher/full-episodes/season-01/episode-00/pilot',
        'only_matching': True,
    }, {
        'url': 'http://www.wetv.com/shows/million-dollar-matchmaker/season-01/episode-06-the-dumped-dj-and-shallow-hal',
        'only_matching': True,
    }, {
        'url': 'http://www.ifc.com/movies/chaos',
        'only_matching': True,
    }, {
        'url': 'http://www.bbcamerica.com/shows/doctor-who/full-episodes/the-power-of-the-daleks/episode-01-episode-1-color-version',
        'only_matching': True,
    }, {
        'url': 'http://www.wetv.com/shows/mama-june-from-not-to-hot/full-episode/season-01/thin-tervention',
        'only_matching': True,
    }, {
        'url': 'http://www.wetv.com/shows/la-hair/videos/season-05/episode-09-episode-9-2/episode-9-sneak-peek-3',
        'only_matching': True,
    }]

    def _real_extract(self, url):
        display_id = self._match_id(url)
        webpage = self._download_webpage(url, display_id)
        query = {
            'mbr': 'true',
            'manifest': 'm3u',
        }
        media_url = self._search_regex(
            r'window\.platformLinkURL\s*=\s*[\'"]([^\'"]+)',
            webpage, 'media url')
        theplatform_metadata = self._download_theplatform_metadata(self._search_regex(
            r'link\.theplatform\.com/s/([^?]+)',
            media_url, 'theplatform_path'), display_id)
        info = self._parse_theplatform_metadata(theplatform_metadata)
        video_id = theplatform_metadata['pid']
        title = theplatform_metadata['title']
        rating = try_get(
            theplatform_metadata, lambda x: x['ratings'][0]['rating'])
        auth_required = self._search_regex(
            r'window\.authRequired\s*=\s*(true|false);',
            webpage, 'auth required')
        if auth_required == 'true':
            requestor_id = self._search_regex(
                r'window\.requestor_id\s*=\s*[\'"]([^\'"]+)',
                webpage, 'requestor id')
            resource = self._get_mvpd_resource(
                requestor_id, title, video_id, rating)
            query['auth'] = self._extract_mvpd_auth(
                url, video_id, requestor_id, resource)
        media_url = update_url_query(media_url, query)
        formats, subtitles = self._extract_theplatform_smil(
            media_url, video_id)
        self._sort_formats(formats)
        info.update({
            'id': video_id,
            'subtitles': subtitles,
            'formats': formats,
            'age_limit': parse_age_limit(parse_age_limit(rating)),
        })
        ns_keys = theplatform_metadata.get('$xmlns', {}).keys()
        if ns_keys:
            ns = list(ns_keys)[0]
            series = theplatform_metadata.get(ns + '$show')
            season_number = int_or_none(
                theplatform_metadata.get(ns + '$season'))
            episode = theplatform_metadata.get(ns + '$episodeTitle')
            episode_number = int_or_none(
                theplatform_metadata.get(ns + '$episode'))
            if season_number:
                title = 'Season %d - %s' % (season_number, title)
            if series:
                title = '%s - %s' % (series, title)
            info.update({
                'title': title,
                'series': series,
                'season_number': season_number,
                'episode': episode,
                'episode_number': episode_number,
            })
        return info
