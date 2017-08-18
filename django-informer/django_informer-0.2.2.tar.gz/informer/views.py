# coding: utf-8

"""
informer views
"""

from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import View
from django.conf import settings
from django.contrib.syndication.views import Feed

from informer.checker.base import BaseInformer, InformerException
from informer.models import Raw


class DefaultView(View):
    """
    Health check
    """
    template = 'django-informer-index.html'

    def get(self, request):
        """
        GET /informer/
        """

        interval = getattr(settings, 'DJANGO_INFORMER_PREVENT_SAVE_UNTIL', 0)

        DJANGO_INFORMERS = getattr(settings, 'DJANGO_INFORMERS', ())

        result = {
            'status': 'All systems are operational',
            'result': []
        }

        for namespace, classname in DJANGO_INFORMERS:
            informer = BaseInformer.get_class(namespace, classname)()
            operational, message = informer.check_availability()

            if not operational:
                result['status'] = 'Oh no. Houston we have problemns'

            name = classname.replace('Informer', '').lower()
            urlname = 'informer-%s' % name

            result['result'].append({
                'name': name,
                'operational': operational,
                'message': message,
                'url': reverse(urlname)
            })

        return render(request, self.template, result, content_type='text/html')


class InformerView(View):
    """
    Get results from a specific Informer
    """
    template = 'django-informer-detail.html'

    def get(self, request, namespace, classname):
        """
        GET /informer/:name/
        """
        indicator = classname.replace('Informer', '')

        try:
            informer = BaseInformer.get_class(namespace, classname)()

            operational, message = informer.check_availability()

            measures = informer.get_measures()
            measures = [measure.replace('check_', '') for measure in measures]

            result = {
                'name': indicator,
                'operational': operational,
                'measures': [],
                'message': message
            }

            for measure in measures:
                fields = ['id', 'indicator', 'measure', 'date', 'value']

                data = Raw.objects.filter(
                    indicator=indicator, measure=measure).order_by(
                        '-date').values(*fields)

                urlname = 'informer-%s-%s' % (indicator.lower(), measure)

                result['measures'].append({
                    'name': measure,
                    'url': reverse(urlname),
                    'data': data[0:3]
                })
        except InformerException as error:
            result = {
                'name': indicator,
                'operational': False,
                'measures': [],
                'message': '%s' % error
            }

        return render(request, self.template, result, content_type='text/html')


class MeasureView(View):
    """
    Get result from a specific measure
    """
    template = 'django-informer-measure.html'

    def get(self, request, namespace, classname, measure):
        """
        GET /informer/:informer/:measure/
        """
        indicator = classname.replace('Informer', '')

        try:
            fields = ['id', 'indicator', 'measure', 'date', 'value']

            data = Raw.objects.filter(
                indicator=indicator, measure=measure).values(*fields)

            result = {
                'indicator': indicator,
                'measure': measure,
                'measures': list(data)
            }
        except Exception as error:
            message = 'error trying get indicator ({0}) or measure ({1})'
            message = message.format(indicator, measure)

            result = {
                'indicator': message,
                'measure': message,
                'measures': []
            }

        return render(request, self.template, result, content_type='text/html')


class InformerFeed(Feed):
    title = 'Django Informer'
    link = '/informer/feed/'
    description = 'Latest data collected by Django Informer'

    def items(self):
        return Raw.objects.order_by('-date')[:10]

    def item_title(self, item):  # pragma: no cover
        return '{0} ({1})'.format(item.indicator, item.measure)

    def item_description(self, item):  # pragma: no cover
        return '{0} collected on {1}'.format(item.value, item.date)

    def item_link(self, item):  # pragma: no cover
        return reverse('feed-informer')
