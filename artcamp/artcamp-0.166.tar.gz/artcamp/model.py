"""docstring."""


from difflib import get_close_matches

from sklearn.pipeline import Pipeline

from cleaner import TextProcessor
from lsi import GensimLsi
from vectorizers import GensimTfidf

import pickle

# with open("org_data.pkl", 'rb') as fp:
#     data = pickle.load(fp)
# with open("name_list.pkl", 'rb') as fp:
#     data_names = pickle.load(fp)
path = os.path.join(os.path.dirname(__file__), 'data/org_data.pkl')
with open(path, 'rb') as fp:
    data_names = pickle.load(fp)
path = os.path.join(os.path.dirname(__file__), 'data/name_list.pkl')
with open(path, 'rb') as fp:
    data_names = pickle.load(fp)

TFIDF = 'tfidf.pkl'
LSI = "test_lsi.pkl"
INDEX = "test_index.pkl"
ID2WORD = "tfidf_dict.pkl"


class OrgSim():
    """Find Org most similar to Article."""

    def __init__(self, lsi_path=LSI, id2word_path=ID2WORD, index_path=INDEX,
                 tfidf_path=TFIDF, org_data=data, name_list=data_names):
        """
        Initialize class.

        Parameters
        ----------
        lsi_path : str
            Path to location of saved gensim LsiModel.
            If specified, the model will load and use this object
            as its LsiModel.
        dict_path : str
            Path to location of saved gensim Dictionary.
            If specified, the model will load and use this object
            as its Dictionary.
        tfidf_path: str
            File-path designating where self.tfidf should be saved.
        org_data: list
            List of data.
        name_list: list
            List of names.
        """
        self.org_data = org_data
        self.name_list = name_list
        self.processor = TextProcessor()
        self.tfidf = GensimTfidf(tfidf_path=tfidf_path,
                                 dictionary_path=id2word_path,
                                 use_sparse_representation=True)
        self.lsi = GensimLsi(lsi_path=lsi_path,
                             id2word_path=id2word_path,
                             index_path=index_path)
        self.transformer = Pipeline([
            ('norm', self.processor),
            ('tfidf', self.tfidf)])

    @staticmethod
    def closest_match(string1, strings):
        """
        Return the most similar org in name_list.

        Parameters
        ----------
        string1: str
            String being queried.
        strings: list
            List of org names.
        """
        result = get_close_matches(string1, strings)
        try:
            return result[0]
        except IndexError:
            return "Not Found"

    def resolve_query(self, org):
        """
        Find most similar org to 'org'.

        Parameters
        ----------
        org: str
            Name of organizatin to query.
        """
        if org in set(self.name_list):
            correct_org = org
        else:
            correct_org = self.closest_match(org, self.name_list)
        # return associated data
        return correct_org, self.name_list.index(correct_org)

    def similarity(self, org, n=10):
        """
        Return the 10 most similar orgs to org.

        Parameters
        ----------
        org: string
            Name of org to query.
        n: int
            Number of orgs to return.

        Returns
        -------
            list: tuples of (org, similarity).
        """
        doc, idx = self.resolve_query(org)
        if doc == "Not Found":
            return "Org not found, please search for another name."
        # Find data associated with doc before returning anything
        doc_data = self.org_data[idx]
        tfidf_data = self.transformer.transform([doc_data])
        return self.lsi.similarity(doc=tfidf_data[0], n=n)


class Art2Org():
    """init."""

    pass


class Org2Art():
    """init."""

    pass
