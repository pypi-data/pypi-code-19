from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse_lazy
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import Permission
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.views.generic.base import ContextMixin
from django.views.generic.detail import SingleObjectMixin, DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView
from haystack.generic_views import SearchView
from thorson_wiki.forms import *
from thorson_wiki.models import Article

class NamespaceMixin(ContextMixin):
    """
    A shortcut mixin which adds the namespace to the context.
    """

    def dispatch(self, *args, **kwargs):

        self.namespace_ = kwargs.get('namespace_', '')

        if self.namespace_ not in settings.THORSONWIKI_NAMESPACES:
            raise Http404("Invalid namespace: %s" % self.namespace_)

        self.namespace = settings.THORSONWIKI_NAMESPACES[self.namespace_]

        return super(NamespaceMixin, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):

        context = super(NamespaceMixin, self).get_context_data(**kwargs)

        context['namespace'] = self.namespace
        context['namespace_'] = self.namespace_
        context['namespaces'] = settings.THORSONWIKI_NAMESPACES

        return context

class ArticleViewMixin(NamespaceMixin, SingleObjectMixin):
    """
    A shortcut mixin to use for all object views which operate on Articles.
    """

    model = Article

    def get_queryset(self):

        namespace_ = self.kwargs.get('namespace_', '')

        return self.model.objects.filter(namespace=namespace_)

class ArticleDetailView(DetailView, ArticleViewMixin):
    """
    Displays details on a single article.
    """

    def get_template_names(self):

        templates = settings.THORSONWIKI_NAMESPACES[self.namespace_].get(
            'templates', {}
        )

        temps = templates.get('detail', 'thorson_wiki/article_detail.html')

        if not isinstance(temps, list):
            temps = [temps]

        return temps

    def get(self, request, *args, **kwargs):

        try:
            return super(ArticleDetailView, self).get(request,
                    *args, **kwargs)
        except Http404:
            try:
                namespace = self.namespace_
            except KeyError:
                raise Http404

            return redirect(namespace + ':article_create')

    def render_to_response(self, context, **response_kwargs):

        if self.object.redirect:
            return redirect(self.namespace_ + ':article',
                    slug=slugify(self.object.redirect))
        else:
            return super(ArticleDetailView, self).render_to_response(
                context, **response_kwargs
            )

class ArticleUpdateView(UserPassesTestMixin, UpdateView, ArticleViewMixin):
    """
    Allows users to update articles.
    """

    form_class = ArticleUpdateForm

    def dispatch(self, request, *args, **kwargs):

        self.kwargs = kwargs
        self.object = self.get_object()

        return super(ArticleUpdateView, self).dispatch(request, *args,
                **kwargs)

    def get_template_names(self):
        
        templates = settings.THORSONWIKI_NAMESPACES[self.namespace_].get(
            'templates', {}
        )

        temps = templates.get('update', 'thorson_wiki/article_update.html')

        if not isinstance(temps, list):
            temps = [temps]

        return temps

    def test_func(self):

        return self.object.can_edit(self.request.user)

class ArticleCreateView(LoginRequiredMixin, NamespaceMixin, CreateView):
    """
    Allows users to create articles.
    """

    form_class = ArticleUpdateForm

    def get_template_names(self):

        templates = settings.THORSONWIKI_NAMESPACES[self.namespace_].get(
            'templates', {}
        )

        temps = templates.get('create', 'thorson_wiki/article_create.html')

        if not isinstance(temps, list):
            temps = [temps]

        return temps

    def get_initial(self):

        initial = super(ArticleCreateView, self).get_initial()

        initial['namespace'] = self.namespace_

        return initial

    def get_object(self):

        return Article(namespace=self.namespace_)

    def get_success_url(self):

        return self.object.get_absolute_url()

class ArticleDeleteView(UserPassesTestMixin, DeleteView, ArticleViewMixin):
    """
    Allows users to delete articles.
    """

    def dispatch(self, request, *args, **kwargs):

        # self.object needs to be available before test_func is called
        self.kwargs = kwargs
        self.object = self.get_object()

        return super(ArticleDeleteView, self).dispatch(request, *args,
                **kwargs)

    def test_func(self):

        return self.object.can_edit(self.request.user)

    def get_success_url(self):

        return reverse_lazy(self.namespace_ + ':main')

class ArticleListView(NamespaceMixin, ListView):
    """
    Allows users to view all articles.
    """

    model = Article

    def get_template_names(self):

        templates = settings.THORSONWIKI_NAMESPACES[self.namespace_].get(
            'templates', {}
        )

        temps = templates.get('list', 'thorson_wiki/article_list.html')

        if not isinstance(temps, list):
            temps = [temps]

        return temps

    def get_queryset(self):

        queryset = super(ArticleListView, self).get_queryset()
        queryset = queryset.filter(namespace=self.namespace_)
        queryset = queryset.order_by('title')

        return queryset

# USERS

class UserCreateView(CreateView, NamespaceMixin):

    model = User
    form_class = UserCreateForm

    def dispatch(self, request, *args, **kwargs):

        self.redirect_to = self.get_redirect_url(request, *args, **kwargs)

        return super(UserCreateView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):

        context = super(UserCreateView, self).get_context_data(**kwargs)

        context['next'] = self.redirect_to

        return context

    def get_redirect_url(self, request, *args, **kwargs):

        namespace_ = kwargs.get('namespace_', '')

        return reverse_lazy(namespace_ + ':login')

    def get_success_url(self):

        return self.redirect_to

    def get_template_names(self):

        templates = settings.THORSONWIKI_NAMESPACES[self.namespace_].get(
            'templates', {}
        )

        temps = templates.get('user_create', 'thorson_wiki/user_create.html')

        if not isinstance(temps, list):
            temps = [temps]

        return temps

class UserUpdateView(UpdateView, NamespaceMixin):

    model = User
    form_class = UserUpdateForm

    def get_object(self, queryset=None):

        return self.request.user

    def get_success_url(self):

        return reverse_lazy(self.namespace_ + ':user_update')

    def get_template_names(self):

        templates = settings.THORSONWIKI_NAMESPACES[self.namespace_].get(
            'templates', {}
        )

        temps = templates.get('user_update', 'thorson_wiki/user_update.html')

        if not isinstance(temps, list):
            temps = [temps]

        return temps

class ArticleSearchView(SearchView, NamespaceMixin):

    def get_queryset(self):

        if self.request.method == 'GET':
            namespace_ = self.request.GET.get('namespace', self.namespace_)
        else:
            namespace_ = self.namespace_

        queryset = super(ArticleSearchView, self).get_queryset()

        if namespace_ == 'ALL':
            pass
        else:
            queryset = queryset.filter(namespace__iexact=namespace_)

        return queryset

    def get_template_names(self):

        templates = settings.THORSONWIKI_NAMESPACES[self.namespace_].get(
            'templates', {}
        )

        temps = templates.get('search', 'thorson_wiki/search.html')

        if not isinstance(temps, list):
            temps = [temps]

        return temps

article_detail = ArticleDetailView.as_view()
article_create = ArticleCreateView.as_view()
article_update = ArticleUpdateView.as_view()
article_delete = ArticleDeleteView.as_view()
article_list = ArticleListView.as_view()

register = UserCreateView.as_view()
user_update = UserUpdateView.as_view()

search = ArticleSearchView.as_view()
