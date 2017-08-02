from collections.abc import Sequence
from datetime import date, datetime

__all__ = ['SeriesSearchData']


class BaseModel:
    def __init__(self, fields, **kwargs):
        self._attrs = {f:self.__class__._apply_func_or_none(transform, kwargs.get(f))
                       for f, transform in fields.items() if f in kwargs}

    @staticmethod
    def _apply_func_or_none(func, arg):
        if arg == [] or arg == '':
            return arg
        if arg is None:
            return None
        return func(arg)


class SeriesSearchData(BaseModel):
    def __init__(self, fields=None, **kwargs):
        fields = fields or {}
        super(SeriesSearchData, self).__init__({**{
            'aliases': list,
            'banner': str,
            'firstAired': lambda s: date(*map(int, s.split('-'))),
            'id': int,
            'network': str,
            'overview': str,
            'seriesName': str,
            'status': str
        }, **fields}, **kwargs)

    @property
    def aliases(self):
        return self._attrs.get('aliases')

    @property
    def banner(self):
        return self._attrs.get('banner')

    @property
    def first_aired(self):
        return self._attrs.get('firstAired')

    @property
    def id(self):
        return self._attrs.get('id')

    @property
    def network(self):
        return self._attrs.get('network')

    @property
    def overview(self):
        return self._attrs.get('overview')

    @property
    def series_name(self):
        return self._attrs.get('seriesName')

    @property
    def status(self):
        return self._attrs.get('status')


class SeriesData(SeriesSearchData):
    def __init__(self, **kwargs):
        super(SeriesData, self).__init__(fields={
            'added': lambda s: datetime.strptime(s, '%Y-%m-%d %H:%M:%S'),
            'airsDayOfWeek': str,
            'airsTime': str,
            'genre': list,
            'imdbId': str,
            'lastUpdated': lambda s: datetime.fromtimestamp(s),
            'networkId': str,
            'rating': str,
            'runtime': str,
            'seriesId': int,
            'siteRating': float,
            'siteRatingCount': int,
            'zap2itId': str
        }, **kwargs)

    @property
    def added(self):
        return self._attrs.get('added')

    @property
    def airs_day_of_week(self):
        return self._attrs.get('airsDayOfWeek')

    @property
    def airs_time(self):
        return self._attrs.get('airsTime')

    @property
    def genre(self):
        return self._attrs.get('genre')

    @property
    def imdb_id(self):
        return self._attrs.get('imdbId')

    @property
    def last_updated(self):
        return self._attrs.get('lastUpdated')

    @property
    def network_id(self):
        return self._attrs.get('networkId')

    @property
    def rating(self):
        return self._attrs.get('rating')

    @property
    def runtime(self):
        return self._attrs.get('runtime')

    @property
    def series_id(self):
        return self._attrs.get('seriesId')

    @property
    def site_rating(self):
        return self._attrs.get('siteRating')

    @property
    def site_rating_count(self):
        return self._attrs.get('siteRatingCount')

    @property
    def zap2it_id(self):
        return self._attrs.get('zap2itId')


class SeriesActorsData(BaseModel):
    def __init__(self, **kwargs):
        super(SeriesActorsData, self).__init__({
            'id': int,
            'image': str,
            'imageAdded': lambda s: datetime.strptime(s, '%Y-%m-%d %H:%M:%S'),
            'imageAuthor': int,
            'lastUpdated': lambda s: datetime.strptime(s, '%Y-%m-%d %H:%M:%S'),
            'name': str,
            'role': str,
            'seriesId': int,
            'sortOrder': int
        }, **kwargs)

    @property
    def id(self):
        return self._attrs.get('id')

    @property
    def image(self):
        return self._attrs.get('image')

    @property
    def image_added(self):
        return self._attrs.get('imageAdded')

    @property
    def image_author(self):
        return self._attrs.get('imageAuthor')

    @property
    def last_updated(self):
        return self._attrs.get('lastUpdated')

    @property
    def name(self):
        return self._attrs.get('name')

    @property
    def role(self):
        return self._attrs.get('role')

    @property
    def series_id(self):
        return self._attrs.get('seriesId')

    @property
    def sort_order(self):
        return self._attrs.get('sortOrder')


class SeriesEpisodes(Sequence):
    def __init__(self, items):
        self._items = items

    def __getitem__(self, index):
        return self._items.__getitem__(index)

    def __len__(self):
        return self._items.__len__()

    def query(self, absolute_number=None, aired_season=None, aired_episode=None, dvd_season=None, dvd_episode=None):
        """
        Filters the episodes for the series according to the provided fields.

        :param absolute_number:
        :param aired_season:
        :param aired_episode:
        :param dvd_season:
        :param dvd_episode:
        :return: A list of episode objects for the current series that match the provided criteria
        """
        def episodes_filter_func(episode):
            if absolute_number is not None and episode.absolute_number != absolute_number:
                return False
            if aired_season is not None and episode.aired_season != aired_season:
                return False
            if aired_episode is not None and episode.aired_episode_number != aired_episode:
                return False
            if dvd_season is not None and episode.dvd_season != dvd_season:
                return False
            if dvd_episode is not None and episode.dvd_episode_number != dvd_episode:
                return False
            return True
        return SeriesEpisodes(list(filter(episodes_filter_func, self._items)))


class BasicEpisode(BaseModel):
    def __init__(self, fields=None, **kwargs):
        fields = fields or {}
        super(BasicEpisode, self).__init__({**{
            'absoluteNumber': int,
            'airedEpisodeNumber': int,
            'airedSeason': int,
            'dvdEpisodeNumber': int,
            'dvdSeason': int,
            'episodeName': str,
            'firstAired': lambda s: date(*map(int, s.split('-'))),
            'id': int,
            'lastUpdated': lambda s: datetime.fromtimestamp(s),
            'overview': str
        }, **fields}, **kwargs)

    @property
    def absolute_number(self):
        return self._attrs.get('absoluteNumber')

    @property
    def aired_episode_number(self):
        return self._attrs.get('airedEpisodeNumber')

    @property
    def aired_season(self):
        return self._attrs.get('airedSeason')

    @property
    def dvd_episode_number(self):
        return self._attrs.get('dvdEpisodeNumber')

    @property
    def dvd_season(self):
        return self._attrs.get('dvdSeason')

    @property
    def episode_name(self):
        return self._attrs.get('episodeName')

    @property
    def first_aired(self):
        return self._attrs.get('firstAired')

    @property
    def id(self):
        return self._attrs.get('id')

    @property
    def last_updated(self):
        return self._attrs.get('lastUpdated')

    @property
    def overview(self):
        return self._attrs.get('overview')


class Episode(BasicEpisode):
    def __init__(self, **kwargs):
        super(Episode, self).__init__({
            'airsAfterSeason': int,
            'airsBeforeEpisode': int,
            'airsBeforeSeason': int,
            'director': str,
            'directors': list,
            'dvdChapter': float,
            'dvdDiscid': str,
            'guestStars': list,
            'lastUpdatedBy': int,
            'productionCode': str,
            'seriesId': int,
            'showUrl': str,
            'thumbAdded': str,
            'thumbAuthor': int,
            'thumbHeight': str,
            'thumbWidth': str,
            'writers': list
        }, **kwargs)

    @property
    def airs_after_season(self):
        return self._attrs.get('airsAfterSeason')

    @property
    def airs_before_episode(self):
        return self._attrs.get('airsBeforeEpisodeon')

    @property
    def airs_before_season(self):
        return self._attrs.get('airsBeforeSeason')

    @property
    def director(self):
        return self._attrs.get('director')

    @property
    def directors(self):
        return self._attrs.get('directors')

    @property
    def dvd_chapter(self):
        return self._attrs.get('dvdChapter')

    @property
    def dvd_disc_id(self):
        return self._attrs.get('dvdDiscid')

    @property
    def guest_stars(self):
        return self._attrs.get('guestStars')

    @property
    def last_updated_by(self):
        return self._attrs.get('lastUpdatedBy')

    @property
    def production_code(self):
        return self._attrs.get('productionCode')

    @property
    def series_id(self):
        return self._attrs.get('seriesId')

    @property
    def show_url(self):
        return self._attrs.get('showUrl')

    @property
    def thumb_added(self):
        return self._attrs.get('thumbAdded')

    @property
    def thumb_author(self):
        return self._attrs.get('thumbAuthor')

    @property
    def thumb_height(self):
        return self._attrs.get('thumbHeight')

    @property
    def thumb_width(self):
        return self._attrs.get('thumbWidth')

    @property
    def writers(self):
        return self._attrs.get('writers')


class SeriesEpisodesSummary(BaseModel):
    def __init__(self, **kwargs):
        super(SeriesEpisodesSummary, self).__init__({
            'airedEpisodes': int,
            'airedSeasons': list,
            'dvdEpisodes': int,
            'dvdSeasons': list
        }, **kwargs)

    @property
    def aired_episodes(self):
        return self._attrs.get('airedEpisodes')

    @property
    def aired_seasons(self):
        return self._attrs.get('airedSeasons')

    @property
    def dvd_episodes(self):
        return self._attrs.get('dvdEpisodes')

    @property
    def dvd_seasons(self):
        return self._attrs.get('dvdSeasons')