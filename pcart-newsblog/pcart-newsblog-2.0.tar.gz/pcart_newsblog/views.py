from django.shortcuts import render, get_object_or_404
from django.http import Http404
from django.utils import timezone
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .models import Category, Article


def articles_view(request):
    articles = Article.objects.filter(published=True, pub_date__lte=timezone.now()).order_by('-pub_date')
    category = request.GET.get('category')
    if category is not None and Category.objects.filter(slug=category).exists():
        articles = articles.filter(category__slug=category)

    paginator = Paginator(articles, per_page=10)
    page = request.GET.get('page')

    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
        articles = paginator.page(1)
    except EmptyPage:
        articles = paginator.page(paginator.num_pages)

    context = {
        'page_url': request.path,
        'articles': articles,
    }
    return render(request, 'newsblog/articles.html', context)


def article_view(request, article_slug):
    article = get_object_or_404(Article, slug=article_slug)
    preview = 'preview' in request.GET

    if not preview:
        if not article.published:
            raise Http404
        elif article.published and article.pub_date > timezone.now():
            raise Http404

    context = {
        'page_url': request.path,
        'article': article,
        'categories': Category.objects.all(),
    }
    return render(request, 'newsblog/article.html', context)
