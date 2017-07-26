from taggit import utils

from django import template
from django.utils import timezone

from ..models import Event

register = template.Library()


@register.assignment_tag
def get_upcoming_events(count=5, category='', tags='', location=''):
    event_list = Event.objects.published().filter(start__gt=timezone.now())

    # Optional filter by category
    if category.strip():
        event_list = event_list.filter(category__slug=category)

    # Optional filter by tags
    if tags.strip(): 
        event_list = event_list.filter(tags__name__in=utils.parse_tags(tags))

    # Optional filter by location
    if location.strip():
        event_list = event_list.filter(locations__title=location)

    return event_list[:count]
