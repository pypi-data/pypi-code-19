import re
from pattern.search import Classifier, Taxonomy
from .es import ContactParent as BaseContactParent, Patterns
from .extractor import EntitiesExtractor


class ContactParent(BaseContactParent):
    PHONE_NUMBER_REGEX = re.compile(r'(\d{2}[\d\-\(\)\s]{3,}\d{2})', re.VERBOSE | re.IGNORECASE)


class Extractors(object):
    @staticmethod
    def create_contact_extractor():
        taxonomy = Taxonomy()
        taxonomy.classifiers.append(Classifier(ContactParent()))
        patterns = Patterns.create_contact_patterns(taxonomy)
        return EntitiesExtractor(patterns)
