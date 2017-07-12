from viewflow import flow, frontend
from viewflow.base import this, Flow
from viewflow.flow.views import DetailProcessView, CreateProcessView, UpdateProcessView

from npolling.models import RyanAirHolidaysScrapeProcess
from django.utils.translation import ugettext_lazy as _


@frontend.register
class RyanAirHolidaysFlow(Flow):
    process_class = RyanAirHolidaysScrapeProcess
    process_title = _('RyanAir Holidays Comparison')
    process_description = _('Report for the cheapest travels.')

    start = (flow.Start(CreateProcessView, fields=[
        'brand',
        'competitor0',
        'competitor1',
        'competitor2',
        'competitor3',
        'language',
        'departure_airport',
        'destination',
        'number_of_adult_travellers',
        'period_earliest_departure',
        'period_latest_return',
        'duration'
    ])
             .Permission(auto_create=True)
             .Next(this.schedule))

    schedule = (flow.Handler(this.scrape)
                .Next(this.results))

    results = (flow.View(UpdateProcessView)
               .Permission(auto_create=True)
               .Next(this.end))

    end = flow.End()

    def scrape(self, activation):
        # TODO: call scrape
        # print(activation.process.text)
        pass
