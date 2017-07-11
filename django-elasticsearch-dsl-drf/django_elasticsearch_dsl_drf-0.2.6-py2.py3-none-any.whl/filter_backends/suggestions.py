"""
Suggestions backend.
"""

from six import string_types

from rest_framework.filters import BaseFilterBackend

__title__ = 'django_elasticsearch_dsl_drf.filter_backends.suggestions'
__author__ = 'Artur Barseghyan <artur.barseghyan@gmail.com>'
__copyright__ = '2016-2017 Artur Barseghyan'
__license__ = 'GPL 2.0/LGPL 2.1'
__all__ = ('SuggestionsFilterBackend',)


class SuggestionsFilterBackend(BaseFilterBackend):
    """Suggestions filter backend for Elasticsearch.

    Example:

        >>> from django_elasticsearch_dsl_drf.filter_backends import (
        >>>     SuggestionsFilterBackend
        >>> )
        >>> from django_elasticsearch_dsl_drf.views import BaseDocumentViewSet
        >>>
        >>> # Local article document definition
        >>> from .documents import ArticleDocument
        >>>
        >>> # Local article document serializer
        >>> from .serializers import ArticleDocumentSerializer
        >>>
        >>> class ArticleDocumentView(BaseDocumentViewSet):
        >>>
        >>>     document = ArticleDocument
        >>>     serializer_class = ArticleDocumentSerializer
        >>>     filter_backends = [SuggestionsFilterBackend,]
        >>>     suggestions_fields = {
        >>>         'title_suggest': 'title.raw',  # Simple, `term` as default
        >>>         'title_suggest_term': {
        >>>             'field': 'title.raw',
        >>>             'suggester': 'term',  # Use `term` suggester
        >>>         },
        >>>         'title_suggest_phrase': {
        >>>             'field': 'title.raw',
        >>>             'suggester': 'phrase',  # Use `phrase` suggester
        >>>         },
        >>>         'title_suggest_autocomplete': {
        >>>             'field': 'title.raw',
        >>>             'suggester': 'completion',  # Use `complete` suggester
        >>>         },
        >>>     }
    """

    suggestion_param = 'suggest'

    def get_suggestions_query_params(self, request, view):
        """Get suggestions query params.

        :param request: Django REST framework request.
        :param view: View.
        :type request: rest_framework.request.Request
        :type view: rest_framework.viewsets.ReadOnlyModelViewSet
        :return: Ordering params to be used for ordering.
        :rtype: list
        """
        query_params = request.query_params.copy()
        ordering_query_params = query_params.getlist(self.suggestion_param, [])

        # Remove invalid ordering query params
        for query_param in ordering_query_params:
            __key = query_param.lstrip('-')
            if __key not in view.ordering_fields:
                ordering_query_params.remove(query_param)

        # If no valid ordering params specified, fall back to `view.ordering`
        if not ordering_query_params:
            return self.get_default_ordering_params(view)

        return ordering_query_params

    def filter_queryset(self, request, queryset, view):
        """Filter the queryset.

        :param request: Django REST framework request.
        :param queryset: Base queryset.
        :param view: View.
        :type request: rest_framework.request.Request
        :type queryset: elasticsearch_dsl.search.Search
        :type view: rest_framework.viewsets.ReadOnlyModelViewSet
        :return: Updated queryset.
        :rtype: elasticsearch_dsl.search.Search
        """
        suggestions_query_params = self.get_suggestions_query_params(
            request,
            view
        )

        if suggestions_query_params:
            return queryset.sort(*suggestions_query_params)

        return queryset
