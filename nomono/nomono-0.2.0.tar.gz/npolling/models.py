from django.db import models
from viewflow.models import Process
from django.utils.translation import ugettext_lazy as _
from nmdm import models as mdm_models

# Create your models here.


class ComparisonReport(models.Model):


    trip = models.ForeignKey(mdm_models.Trip)

    flight_only_price_with_bags = models.ForeignKey(mdm_models.ComparisonRecord, related_name='flight_only_price_with_bags')
    hotel_only_price_per_person = models.ForeignKey(mdm_models.ComparisonRecord, related_name='hotel_only_price_per_person')
    bag_price_per_person = models.ForeignKey(mdm_models.ComparisonRecord, related_name='bag_price_per_person')
    package_price_without_bags = models.ForeignKey(mdm_models.ComparisonRecord, related_name='package_price_without_bags')
    package_price_with_bags = models.ForeignKey(mdm_models.ComparisonRecord, related_name='package_price_with_bags')


class RyanAirHolidaysScrapeProcess(Process):
    # 1. Select brand
    brand = models.ForeignKey(mdm_models.Brand)
    # 2. Select language
    language = models.CharField(max_length=150, choices=mdm_models.RYANAIR_HOLIDAYS_LANGUAGES)
    # Define competitors
    competitor0 = models.ForeignKey(mdm_models.Brand, related_name='competitor0')
    competitor1 = models.ForeignKey(mdm_models.Brand, related_name='competitor1')
    competitor2 = models.ForeignKey(mdm_models.Brand, related_name='competitor2')
    competitor3 = models.ForeignKey(mdm_models.Brand, related_name='competitor3')

    # 3. Add departure airport
    departure_airport = models.ForeignKey(mdm_models.Airport)

    # 4. Add destination
    # TODO: Need to get the list of destinations from Client, It means regions
    destination = models.ForeignKey(mdm_models.City)

    # 5. Select number of travellers
    number_of_adult_travellers = models.IntegerField(default=2)

    # 6. Select period
    # TODO: It is given by client, probably 8 dates, and rolled forward week by week.
    period_earliest_departure = models.DateTimeField()
    # TODO: Calculated data based on duration and earliest departure date given by Client
    period_latest_return = models.DateTimeField()

    # 7. Select duration
    # TODO: Given by Client, usually 3, 7 or 14 days
    duration = models.IntegerField()

    # 8. Hit search
    hit_search_xpath = models.CharField(max_length=120)

    # 9. Iterate all hotels

    # 10. select a hotel
    # 11. select a board
    # 12. Actual selection (room type - Any, means it will be the cheapest) is ok, click "Go"
    # 13. Check selected Duration, Departure Airport, Month and Day
    # Store Departure time of Outward flight and departure time of Return flight
    # Store number of Stars
    # Hit go
    # 14. Go to supploer summary page
    # Accomodation details:
    # Check departure date, duration
    # Check Travellers
    # Store Room Type
    # Store Board Type
    # Flight details:
    # Check departure date outbound
    # Check departure time outbound
    # Check departure date inbound
    # Check departure time inbound
    # Transfer section:
    # Store Transfer Price
    # Select without Transfer
    # Summary
    # Store Total price
    # 15. Bag section:
    # Click "Add to trip"
    # Store 15 kg bag's price
    # Store 20 kg bag's price
    # Clieck "Cancel"
    # 16 Take screenshot



    verbose_name = _('RyanAir holidays')
