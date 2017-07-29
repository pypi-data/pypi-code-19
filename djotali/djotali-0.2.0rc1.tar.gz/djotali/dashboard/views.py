# coding: utf-8
from django.views import generic

from djotali.campaigns.models import Campaign, Notification
from djotali.core.utils import is_celery_running
from djotali.contacts.models import Contact


class IndexView(generic.TemplateView):
    template_name = 'dashboard/index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['total_campaings'] = Campaign.objects.count()
        context['total_contacts'] = Contact.objects.count()
        context['is_broker_running'] = is_celery_running()
        context['total_messages'] = Notification.objects.filter(status=1).count()
        context['campaigns'] = Campaign.objects.all()[:5]
        return context
