from django.views.generic.detail import DetailView

from listing.models import Listing


class ListingDetail(DetailView):
    model = Listing
    template_name = "listing/listing_detail.html"

    def get_queryset(self):
        return Listing.permitted.all()
