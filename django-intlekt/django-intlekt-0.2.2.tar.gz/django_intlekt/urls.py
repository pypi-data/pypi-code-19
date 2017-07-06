from django.conf.urls import include, url
from rest_framework_mongoengine.routers import DefaultRouter
from rest_framework_nested.routers import NestedSimpleRouter

from . import views


router = DefaultRouter()

router.register(r'collections', views.collections.CollectionViewSet)
router.register(r'documents', views.collections.DocumentViewSet)
router.register(r'sources', views.collections.SourceViewSet)
router.register(r'source_drivers', views.collections.SourceDriverViewSet)
router.register(r'tags', views.collections.TagViewSet)

router.register(r'glossary', views.library.GlossaryViewSet)
router.register(r'lexicon', views.library.LexiconViewSet)
router.register(r'texts', views.library.TextViewSet)
router.register(r'usls', views.library.USLViewSet)
router.register(r'words', views.library.WordViewSet)

posts_router = NestedSimpleRouter(router, r'collections', lookup='collection')
posts_router.register(
    r'posts',
    views.collections.PostViewSet,
    base_name='collection_posts',
)

collected_sources_router = NestedSimpleRouter(router, r'collections', lookup='collection')
collected_sources_router.register(
    r'sources',
    views.collections.CollectedSourceViewSet,
    base_name='collection_collected_sources',
)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^', include(posts_router.urls)),
    url(r'^', include(collected_sources_router.urls)),

    # TODO: to be removed, for testing
    url(r'^ui/$', views.home),
    url(r'^ui/usl_tagger$', views.usl_tagger),
    url(r'^scoopit/$', views.scoopit),
]
