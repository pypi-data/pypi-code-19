from trunity_3_client import TermsClient
from bs4 import BeautifulSoup


class Glossary(object):

    def __init__(self, site_id, session):
        self._site_id = site_id
        self._client = TermsClient(session)

    def _upload_term(self, term: str, definition: str) -> str:
        """
        Upload term to T3 and return term id.
        """
        print("Glossary term - {}: {}".format(term, definition))

        return self._client.list.post(
            site_id=self._site_id,
            term_title=term,
            term_text=definition,
        )

    @staticmethod
    def _get_term(term_tag):
        term = term_tag['data-word']
        definition_tag = term_tag.find(
            "span",
            attrs={"data-type": "glossaryDefinition"}
        )

        # sometimes we have glossary terms without definitions.
        # this prevent the program from crushing:
        if definition_tag:
            definition = definition_tag.text
        else:
            definition = ''

        return term.strip(), definition.strip()

    @staticmethod
    def _build_t3_term_tag(soup, term_id, term):
        new_tag = soup.new_tag("term")
        new_tag.string = term
        new_tag["content-term-id"] = str(term_id)
        return new_tag

    def fix_tags(self, html: str) -> str:
        """
        - find all occurrences of term in html
        - upload term and definition to Trunity 3
        - fix html according to T3 format

        :param html article source html from Trunity 2:
        :return: str
        """
        soup = BeautifulSoup(html,  "html.parser")

        for term_tag in soup.find_all("span", class_='trunity_glossary'):
            term, definition = self._get_term(term_tag)
            term_id = self._upload_term(term, definition)
            t3_tag = self._build_t3_term_tag(soup, term_id, term)
            term_tag.replace_with(t3_tag)

        return soup.decode()
