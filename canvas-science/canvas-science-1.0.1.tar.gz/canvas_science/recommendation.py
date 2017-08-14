class Recommendation(object):

    def __init__(self, *args, title, status_display, narrative, **kwargs):
        self.title = title
        self.status_display = status_display
        self.narrative = narrative

    def to_json(self):
        pass


class VaccineRecommendation(Recommendation):

    pass
