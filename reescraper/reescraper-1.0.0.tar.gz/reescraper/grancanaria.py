from .core import Scraper


class GranCanaria(Scraper):

    def __init__(self, session=None):
        super().__init__(session)

    def get(self):
        return super().get("GCANARIA", "Atlantic/Canary")


