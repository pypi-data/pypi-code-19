from haystack import indexes
from thorson_wiki.models import Article

class ArticleIndex(indexes.SearchIndex, indexes.Indexable):

    text = indexes.CharField(document=True, use_template=True)
    namespace = indexes.CharField(model_attr='namespace')

    def get_model(self):

        return Article
