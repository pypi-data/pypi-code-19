class SMMRY:
    def __init__(self, data):
        self._length = data.get('sm_api_character_count')
        self._title = data.get('sm_api_title')
        self._content = data.get('sm_api_content')
        self._keywords = data.get('sm_api_keyword_array', [])

    @property
    def length(self):
        return self._length

    @property
    def title(self):
        return self._title

    @property
    def content(self):
        return self._content

    @property
    def keywords(self):
        return self._keywords
