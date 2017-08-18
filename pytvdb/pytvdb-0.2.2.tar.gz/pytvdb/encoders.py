from json import JSONEncoder

from datetime import date


class TvdbJSONEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, date):
            return str(o)
        return super(TvdbJSONEncoder, self).default(o)