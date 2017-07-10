from copy import copy
from django import template

from molo.yourtips.models import YourTip, YourTipsArticlePage

register = template.Library()


@register.inclusion_tag(
    'yourtips/your_tips_on_homepage.html',
    takes_context=True
)
def your_tips_on_homepage(context):
    context = copy(context)
    if get_your_tip(context):

        tip_on_homepage = YourTipsArticlePage.objects.filter(
            featured_in_homepage=True).order_by(
                '-featured_in_homepage_start_date').first()

        if not tip_on_homepage:
            tip_on_homepage = YourTipsArticlePage.objects.all().order_by(
                '-latest_revision_created_at').first()

        most_popular_tip = YourTipsArticlePage.objects.filter(
            votes__gte=1
        ).order_by('-total_upvotes').first()

        context.update({
            'most_popular_tip': most_popular_tip,
            'article_tip': tip_on_homepage,
            'your_tip_page_slug': get_your_tip(context).slug
        })
    return context


@register.inclusion_tag(
    'yourtips/your_tips_on_tip_submission_form.html',
    takes_context=True
)
def your_tips_on_tip_submission_form(context):
    context = copy(context)

    most_recent_tip = YourTipsArticlePage.objects.all(
    ).order_by('-latest_revision_created_at').first()

    most_popular_tip = YourTipsArticlePage.objects.filter(
        votes__gte=1
    ).order_by('-total_upvotes').first()

    context.update({
        'most_popular_tip': most_popular_tip,
        'most_recent_tip': most_recent_tip,
        'your_tip_page_slug': get_your_tip(context).slug
    })
    return context


@register.inclusion_tag(
    'yourtips/your_tips_create_tip_on_homepage.html',
    takes_context=True
)
def your_tips_create_tip_on_homepage(context):
    context = copy(context)
    if get_your_tip(context):
        homepage_action_copy = get_your_tip(context).homepage_action_copy
        context.update({
            'your_tip_page_slug': get_your_tip(context).slug,
            'homepage_action_copy': homepage_action_copy
        })
    return context


@register.inclusion_tag(
    'yourtips/your_tips_breadcrumbs.html',
    takes_context=True
)
def your_tips_breadcrumbs(context, active_breadcrumb_title=None):
    context = copy(context)
    if get_your_tip(context):

        context.update({
            'your_tip_page_slug': get_your_tip(context).slug,
            'active_breadcrumb_title': active_breadcrumb_title
        })
    return context


@register.simple_tag(takes_context=True)
def get_your_tip(context):
    return YourTip.objects.first()
