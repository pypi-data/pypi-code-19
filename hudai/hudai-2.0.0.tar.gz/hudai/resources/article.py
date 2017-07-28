from ..resource import Resource


class ArticleResource(Resource):
    def __init__(self, client):
        Resource.__init__(self, client, base_path='/articles')
        self.resource_name = 'Article'

    def list(self,
             type=None,
             published_after=None,
             published_before=None,
             key_term=None,
             link_hash=None,
             importance_score_min=None):
        return self._list(
            type=type,
            published_after=published_after,
            published_before=published_before,
            key_term=key_term,
            link_hash=link_hash,
            importance_score_min=importance_score_min
        )

    def create(self,
               type=None,
               title=None,
               text=None,
               image_url=None,
               link_url=None,
               source_url=None,
               importance_score=None,
               published_at=None,
               raw_location=None,
               authors=[]):
        return self._create(
            type=type,
            title=title,
            text=text,
            image_url=image_url,
            link_url=link_url,
            source_url=source_url,
            importance_score=importance_score,
            published_at=published_at,
            raw_location=raw_location,
            authors=authors
        )

    def get(self, id):
        return self._get(id)

    def update(self, id,
               type=None,
               title=None,
               text=None,
               image_url=None,
               link_url=None,
               source_url=None,
               importance_score=None,
               published_at=None,
               raw_location=None,
               authors=[]):
        return self._update(id,
            type=type,
            title=title,
            text=text,
            image_url=image_url,
            link_url=link_url,
            source_url=source_url,
            importance_score=importance_score,
            published_at=published_at,
            raw_location=raw_location,
            authors=authors
        )

    def delete(self, id):
        return self._delete(id)

    def key_terms(self, id):
        return self.get('/{id}/key-terms', {
            'params': {'id': id}
        })
