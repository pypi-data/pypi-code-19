def extract_name(data):
    # Person object can given response of get_title_by_id
    # or get_person_by_id call.
    # This function covers the slight data structure differences
    # to extract the name
    name = data.get('name')
    if isinstance(name, dict):
        return name.get('name')
    return name


def extract_imdb_id(data):
    name = data.get('name')
    if isinstance(name, dict):
        return name.get('nconst')
    return data.get('nconst')


def extract_photo_url(data):
    return data.get('image', {}).get('url')


def extract_directors_summary(data):
    return [Person(p) for p in data.get('directors_summary', [])]


def extract_creators(data):
    return [Person(p) for p in data.get('creators', [])]


def build_dict(val):
    return {'url': val['url'], 'format': val['format']}


def extract_trailers(data):
    trailers = data.get('trailer', {}).get('encodings', {}).values()
    return [build_dict(trailer) for trailer in trailers]


def extract_writers_summary(data):
    return [Person(p) for p in data.get('writers_summary', [])]


def extract_cast_summary(data):
    return [Person(p) for p in data.get('cast_summary', [])]


def extract_credits(data):
    credits_ = []
    people = data.get('credits')
    if not people:
        return []

    for credit_group in people:
        # Possible tokens: directors, cast, writers, producers and others
        for person in credit_group['list']:
            person_extra = {
                'token': credit_group.get('token'),
                'label': credit_group.get('label'),
                'job': person.get('job'),
                'attr': person.get('attr')
            }
            person_data = person.copy()
            person_data.update(person_extra)
            if 'name' in person_data.keys():
                # some 'special' credits such as script rewrites
                # have different formatting.
                # we skip those here, losing some data due to this check
                credits_.append(Person(person_data))
    return credits_


def extract_year(data):
    return convert_to_int(data.get('year'))


def extract_trailer_image_urls(data):
    slates = data.get('trailer', {}).get('slates', [])
    return [s['url'] for s in slates if 'url' in s]


def convert_to_int(value):
    if not value:
        return
    try:
        return int(value)
    except ValueError:
        return


class Person:
    __slots__ = ('name', 'imdb_id', 'photo_url', 'token', 'label',
                 'attr', 'roles', 'job')

    def __init__(self, data):
        # primary attributes that should be set in all cases

        self.name = extract_name(data)
        self.imdb_id = extract_imdb_id(data)
        self.photo_url = extract_photo_url(data)

        # secondary attribs, will only get data when called via get_title_by_id

        # token and label are the persons categorisation
        # e.g token: writers label: Series writing credits
        self.token = data.get('token')
        self.label = data.get('label')
        # attr is a note about this persons work
        # e.g. (1990 - 1992 20 episodes)
        self.attr = data.get('attr')
        # other primary information about their part
        self.roles = (
            data.get('char').split('/') if data.get('char') else []
        )
        self.job = data.get('job')

    def __repr__(self):
        return '<Person: {0} ({1})>'.format(
            repr(self.name), repr(self.imdb_id)
        )

    def __unicode__(self):
        return '<Person: {0} ({1})>'.format(
            self.name.encode('utf-8'), self.imdb_id
        )


class Title:
    __slots__ = ('imdb_id', 'title', 'type', 'year', 'tagline', 'plots',
                 'plot_outline', 'rating', 'genres', 'votes', 'runtime',
                 'poster_url', 'cover_url', 'release_date', 'certification',
                 'trailer_image_urls', 'directors_summary', 'creators',
                 'cast_summary', 'writers_summary', 'credits', 'trailers')

    def __init__(self, data):
        self.imdb_id = data.get('tconst')
        self.title = data.get('title')
        self.type = data.get('type')
        self.year = extract_year(data)
        self.tagline = data.get('tagline')
        self.plots = data.get('plots')
        self.plot_outline = data.get('plot', {}).get('outline')
        self.rating = data.get('rating')
        self.genres = data.get('genres')
        self.votes = data.get('num_votes')
        self.runtime = data.get('runtime', {}).get('time')
        self.poster_url = data.get('image', {}).get('url')
        self.cover_url = self._extract_cover_url()
        self.release_date = data.get('release_date', {}).get('normal')
        self.certification = data.get('certificate', {}).get('certificate')
        self.trailer_image_urls = extract_trailer_image_urls(data)
        self.directors_summary = extract_directors_summary(data)
        self.creators = extract_creators(data)
        self.cast_summary = extract_cast_summary(data)
        self.writers_summary = extract_writers_summary(data)
        self.credits = extract_credits(data)
        self.trailers = extract_trailers(data)

    def _extract_cover_url(self):
        if self.poster_url:
            return '{0}_SX214_.jpg'.format(self.poster_url.replace('.jpg', ''))

    def __repr__(self):
        return '<Title: {0} - {1}>'.format(
            repr(self.title), repr(self.imdb_id)
        )

    def __unicode__(self):
        return '<Title: {0} - {1}>'.format(self.title, self.imdb_id)


class Image:
    __slots__ = ('caption', 'url', 'width', 'height')

    def __init__(self, data):
        self.caption = data.get('caption')
        self.url = data.get('image', {}).get('url')
        self.width = data.get('image', {}).get('width')
        self.height = data.get('image', {}).get('height')

    def __repr__(self):
        return '<Image: {0}>'.format(repr(self.caption))

    def __unicode__(self):
        return '<Image: {0}>'.format(self.caption.encode('utf-8'))


class Episode:
    __slots__ = ('imdb_id', 'release_date', 'title', 'series_name', 'type',
                 'year', 'season', 'episode')

    def __init__(self, data):
        self.imdb_id = data.get('tconst')
        self.release_date = data.get('release_date', {}).get('normal')
        self.title = data.get('title')
        self.series_name = data.get('series_name')
        self.type = data.get('type')
        self.year = extract_year(data)
        self.season = convert_to_int(data.get('season'))
        self.episode = convert_to_int(data.get('episode'))

    def __repr__(self):
        return '<Episode: {0} - {1}>'.format(repr(self.title),
                                             repr(self.imdb_id))

    def __unicode__(self):
        return '<Episode: {0} - {1}>'.format(self.title, self.imdb_id)


class Review:
    __slots__ = ('username', 'text', 'date', 'rating', 'summary', 'status',
                 'user_location', 'user_score', 'user_score_count')

    def __init__(self, data):
        self.username = data.get('user_name')
        self.text = data.get('text')
        self.date = data.get('date')
        self.rating = data.get('user_rating')
        self.summary = data.get('summary')
        self.status = data.get('status')
        self.user_location = data.get('user_location')
        self.user_score = data.get('user_score')
        self.user_score_count = data.get('user_score_count')

    def __repr__(self):
        return '<Review: {0}>'.format(repr(self.text[:20]))

    def __unicode__(self):
        return '<Review: {0}>'.format(self.text[:20].encode('utf-8'))
