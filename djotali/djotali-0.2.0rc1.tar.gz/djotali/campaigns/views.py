# coding: utf-8
from django.apps import apps
from django.contrib import messages
from django.db.models.aggregates import Sum
from django.db.models.expressions import Case, When
from django.db.models.fields import IntegerField
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.urls.base import reverse
from django.views import generic

from djotali.campaigns.forms import CampaignForm
from djotali.campaigns.models import Campaign, Notification
from djotali.campaigns.tasks import notify_campaign, notify_task, is_campaign_launched
from djotali.core.utils import is_celery_running
from djotali.core.views import paginate_in_context


class IndexView(generic.ListView):
    template_name = 'campaigns/index.html'
    context_object_name = "list_objects"
    paginate_by = 5
    queryset = Campaign.get_closest_campaigns_query_set()


class NotificationsView(generic.DetailView):
    model = Campaign
    template_name = 'campaigns/notifications.html'
    context_object_name = 'campaign'

    def get_context_data(self, **kwargs):
        context = super(NotificationsView, self).get_context_data(**kwargs)
        campaign = self.object

        status = self.request.GET.get('status')
        context["status"] = status

        notifications = campaign.notifications
        if status is not None:
            notifications = notifications.filter(status=Notification.get_status_value(status))
        paginate_in_context(self.request, notifications, context, "notifications")

        context['editable'] = not is_campaign_launched(campaign.id)

        return context


class DetailView(generic.DetailView):
    model = Campaign
    template_name = 'campaigns/show.html'
    context_object_name = 'campaign'

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        broker_running = is_celery_running()

        if not broker_running:
            messages.add_message(self.request, messages.ERROR, "Broker is not running.")
        c = self.object

        context['is_broker_running'] = broker_running

        context['total_notifications'] = c.notifications.count()
        context['editable'] = not is_campaign_launched(c.id)
        context['contacts_group_editable'] = c.contacts_group.id != apps.get_app_config('contacts').all_contacts_group_id

        return context

    def get_queryset(self):
        return super(DetailView, self).get_queryset(). \
            prefetch_related('notifications__contact'). \
            annotate(
            failed=Sum(
                Case(
                    When(notifications__status=-1, then=1),
                    default=0,
                    output_field=IntegerField()
                )
            ),
            sent=Sum(
                Case(
                    When(notifications__status=1, then=1),
                    default=0,
                    output_field=IntegerField()
                )
            ),
            progress=Sum(
                Case(
                    When(notifications__status=0, then=1),
                    default=0,
                    output_field=IntegerField()
                )
            )
        )


class CreateView(generic.CreateView):
    model = Campaign
    template_name = 'campaigns/new.html'
    form_class = CampaignForm

    def get_success_url(self):
        return reverse('campaigns:show', args=[self.object.id])

    def form_valid(self, form):
        response = super(CreateView, self).form_valid(form)

        # We create notifications associated to contacts
        notifications = []
        for contact in self.object.contacts_group.contacts.all():
            notifications.append(Notification(contact=contact, campaign=self.object, status=0))
        Notification.objects.bulk_create(notifications)

        return response


class EditView(generic.UpdateView):
    model = Campaign
    template_name = 'campaigns/edit.html'
    form_class = CampaignForm

    def get_success_url(self):
        return reverse('campaigns:show', args=[self.object.id])


def campaign_notify(request, campaign_id):
    broker_running = is_celery_running()

    if broker_running:
        notify_campaign.delay(campaign_id)

    return HttpResponseRedirect(reverse('campaigns:show', args=(campaign_id,)))


def show_campaign(request, campaign_id):
    c = Campaign.objects. \
        prefetch_related('notifications__contact'). \
        get(pk=campaign_id)

    broker_running = is_celery_running()

    if not broker_running:
        messages.add_message(request, messages.ERROR, "Broker is not running.")
    total = c.notifications.count()
    failed = c.count_failed()
    sent = c.count_sent()
    context = {
        'is_broker_running': broker_running,
        'notifications': c.notifications.all(),
        'campaign': c,
        'failed': failed,
        'sent': sent,
        'in_progress': c.count_unsent(),
        'total_notifications': total,
        'contacts_group_editable': not c.contacts_group.is_all_contacts(),
    }
    return render(request, 'campaigns/show.html', context=context)


def notify(request, campaign_id, notification_id):
    broker_running = is_celery_running()

    if broker_running:
        messages.add_message(request, messages.SUCCESS, "Processing Notification %s !" % notification_id)
        notify_task.delay(campaign_id, notification_id)
    else:
        messages.add_message(request, messages.ERROR, "Oups ! Broker is not running !")

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
